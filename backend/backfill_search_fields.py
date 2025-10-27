# backend/backfill_search_fields.py
from app.db.session import SessionLocal
from app.db.models import Item, Category
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import func, select, text

def run_search_backfill_commit_each():
    print("Starting search field backfill process (category_name_norm, tsv) committing each item...")

    # --- Step 1: Get all Item IDs ---
    try:
        # Use a temporary session just to get IDs
        with SessionLocal() as temp_db:
            item_ids = temp_db.scalars(select(Item.id).order_by(Item.id)).all()
        if not item_ids:
            print("No items found.")
            return
        total_items = len(item_ids)
        print(f"Found {total_items} items to process...")
    except Exception as e:
        print(f"Error fetching item IDs: {e}")
        return

    # --- Step 2: Process each item individually ---
    processed_count = 0
    error_count = 0
    
    # Use ONE session for the whole process, but commit frequently
    db = SessionLocal()
    try:
        for count, item_id in enumerate(item_ids):
            if (count + 1) % 10 == 0: # Print progress
                print(f"Processing item {count + 1}/{total_items}...")

            try:
                # Fetch the single item with its category
                item = (
                    db.query(Item)
                    .options(joinedload(Item.category))
                    .filter(Item.id == item_id)
                    .one_or_none() # Use one_or_none in case an ID is invalid
                )

                if not item:
                    print(f"  Warning: Could not fetch item for ID: {item_id}. Skipping.")
                    error_count += 1
                    continue # Skip to the next item_id

                category_name = item.category.name if item.category else None

                # --- NORMALIZE DATA ---
                name_norm = (item.name or '').lower().strip()
                description_norm = (item.description or '').lower().strip()
                category_name_norm = (category_name or '').lower().strip()

                # --- PREPARE RAW SQL UPDATE ---
                sql = text("""
                    UPDATE items
                    SET name_norm = :name_norm,
                        description_norm = :desc_norm,
                        category_name_norm = :cat_norm,
                        tsv = to_tsvector('simple',
                                  coalesce(:name_norm, '') || ' ' ||
                                  coalesce(:desc_norm, '') || ' ' ||
                                  coalesce(:cat_norm, '')
                              )
                    WHERE id = :item_id
                """)

                params = {
                    "name_norm": name_norm if name_norm else None,
                    "desc_norm": description_norm if description_norm else None,
                    "cat_norm": category_name_norm if category_name_norm else None,
                    "item_id": item.id
                }

                db.execute(sql, params) # Execute the raw SQL
                db.commit() # Commit right after executing
                processed_count += 1

            except Exception as item_error:
                print(f"  Error processing item ID {item_id}: {item_error}")
                print("  Rolling back this item and continuing...")
                db.rollback() # Rollback the failed item
                error_count += 1
                # The loop will continue to the next item

        print(f"\nSearch field backfill completed.")
        print(f"Successfully processed {processed_count} items.")
        if error_count > 0:
            print(f"Skipped {error_count} items due to errors.")
        print("✅")

    except Exception as general_error:
        # Catch any broader errors outside the inner loop
        print(f"\nA general error occurred: {general_error}")
        db.rollback()
    finally:
        db.close() # Ensure the single session is closed at the end


if __name__ == "__main__":
    run_search_backfill_commit_each()