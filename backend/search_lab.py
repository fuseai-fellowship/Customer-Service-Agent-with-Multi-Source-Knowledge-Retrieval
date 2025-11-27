from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from app.db.models import Item
from app.db.session import SessionLocal
from app.core.embedding import get_embedding_model

db= SessionLocal()

def search_fts_simple(db: Session, query: str):
    """
    Simple FTS search using the 'simple' configuration.
    Returns all items that match all words in the query.
    """
    # Convert query into tsquery (AND between words)
    ts_query = func.plainto_tsquery('simple', query.replace(" ", " & "))
    
    # Filter items where tsvector matches the tsquery
    results = db.query(Item).filter(Item.tsv.op('@@')(ts_query)).all()
    
    return results


SIMILARITY_THRESHOLD = 0.3
WEIGHT_CATEGORY = 1.0
WEIGHT_NAME = 0.8
WEIGHT_DESCRIPTION = 0.5

def search_fuzzy_db_weighted(db: Session, query: str):
    """
    Fuzzy search using trigram similarity for all columns.
    Applies column-priority weights and returns max weighted score per row.
    """
    score_category = func.similarity(Item.category_name_norm, query) * WEIGHT_CATEGORY
    score_name = func.similarity(Item.name_norm, query) * WEIGHT_NAME
    score_description = func.similarity(Item.description_norm, query) * WEIGHT_DESCRIPTION

    # Take the max weighted score across all columns
    score = func.greatest(score_category, score_name, score_description)

    results = (
        db.query(Item, score.label("score"))
        .filter(score > SIMILARITY_THRESHOLD)
        .order_by(desc("score"))
        .all()
    )

    return results


# results = search_fuzzy_db_weighted(db, "tortilla chips")
# print(results)


from sqlalchemy import bindparam
from sqlalchemy import asc

SEMANTIC_THRESHOLD = 0.2
SEMANTIC_WEIGHT = 0.4
ROUND = 2

def search_semantic(db: Session, query: str, top_k: int = 15):
    """
    DB-side pgvector semantic search that:
      - passes embedding as a bound param (avoids SQL typing errors)
      - converts distance -> similarity (1 - dist)
      - filters by SEMANTIC_THRESHOLD
      - returns list of (item, similarity_weighted, similarity_raw)
    """
    # 1. get query embedding (list of floats)
    model = get_embedding_model()
    q_emb = model.encode(query)
    if hasattr(q_emb, "tolist"):
        q_emb = q_emb.tolist()

    # 2. create a bind parameter with the embedding value
    emb_param = bindparam("query_embedding", value=q_emb)

    # 3. build distance expression using the bound param
    distance_col = Item.emb.cosine_distance(emb_param).label("dist")  # SQL expr
    similarity_col = (1 - distance_col).label("sim")

    # 4. run the query (note .order_by(distance_col.asc()))
    rows = (
        db.query(Item, distance_col, similarity_col)
          .filter(similarity_col >= SEMANTIC_THRESHOLD)
          .order_by(distance_col.asc())
          .limit(top_k)
          .all()
    )

    # 5. format results and apply weight + rounding
    formatted = []
    for row in rows:
        # row is (Item, dist_val, sim_val)
        item = row[0]
        dist_val = float(row[1])
        sim_val = float(row[2]) if row[2] is not None else 1.0 - dist_val

        sim_raw = sim_val
        sim_weighted = round(sim_raw * SEMANTIC_WEIGHT, ROUND)
        sim_raw_rounded = round(sim_raw, ROUND)
        formatted.append((item, sim_weighted, sim_raw_rounded))

    return formatted
results = search_semantic(db, "tortilla", top_k=10)
for item, weighted_score, raw_score in results:
    print(item.name, weighted_score, raw_score)