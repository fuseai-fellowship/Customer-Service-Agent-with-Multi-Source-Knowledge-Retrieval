from app.db.session import SessionLocal
from app.db.models import KnowledgeBase 
from app.core.embedding import get_embedding_model 

def run_kb_backfill():
    """
    Finds all knowledge_base items with a NULL embedding and generates a new one.
    """
    db = SessionLocal()
    # Get the embedding model (this will load 'all-MiniLM-L6-v2')
    model = get_embedding_model() 
    print("Starting Knowledge Base embedding backfill process...")

    try:
        # Fetch all rows from knowledge_base where 'emb' is NULL
        rows_to_process = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.emb == None)
            .all()
        )

        if not rows_to_process:
            print("No KB items found with missing embeddings. Database is up-to-date. ✅")
            return

        print(f"Found {len(rows_to_process)} KB items to process...")

        count = 0
        for row in rows_to_process:
            count += 1
            print(f"Processing item {count}/{len(rows_to_process)}: Topic '{row.topic}'...")

            # Get the text content from the row
            content_to_embed = row.content

            # Generate the embedding directly from the content
            embedding_vector = model.encode(content_to_embed).tolist()

            # Update the item's 'emb' field
            row.emb = embedding_vector

        # Commit all the changes to the database at once
        print("\nSaving all generated embeddings to the database...")
        db.commit()
        print("KB Backfill completed successfully! All items now have embeddings. ✅")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Rolling back database changes.")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_kb_backfill()