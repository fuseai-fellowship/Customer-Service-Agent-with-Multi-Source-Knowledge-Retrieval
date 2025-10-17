# backend/backfill_embeddings.py
from app.db.session import SessionLocal
from app.db.models import Item, Category
from app.core.embedding import generate_embedding
from sqlalchemy.orm import joinedload

def run_backfill():
    """
    Finds all items with a NULL embedding and generates a new one.
    """
    db = SessionLocal()
    print("Starting embedding backfill process...")

    try:
        # Fetch all items where 'emb' is NULL, and also fetch their related category
        # to avoid extra database queries inside the loop.
        items_to_process = (
            db.query(Item)
            .options(joinedload(Item.category))
            .filter(Item.emb == None)
            .all()
        )

        if not items_to_process:
            print("No items found with missing embeddings. Database is already up-to-date. ✅")
            return

        print(f"Found {len(items_to_process)} items to process...")

        count = 0
        for item in items_to_process:
            count += 1
            print(f"Processing item {count}/{len(items_to_process)}: '{item.name}'...")

            # Prepare the data for the embedding function
            item_data = {
                "name": item.name,
                "description": item.description,
                "subcategory": item.subcategory,
            }
            category_name = item.category.name if item.category else None

            # Generate the embedding
            embedding_vector = generate_embedding(item_data, category_name)

            # Update the item's 'emb' field
            item.emb = embedding_vector

        # Commit all the changes to the database at once
        print("\nSaving all generated embeddings to the database...")
        db.commit()
        print("Backfill completed successfully! All items now have embeddings. ✅")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Rolling back database changes.")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_backfill()