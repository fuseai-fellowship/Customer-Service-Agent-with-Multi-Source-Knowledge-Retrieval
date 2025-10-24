# backend/benchmark_search.py
import time
import statistics
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Item
from app.routers.items import SearchMode  # Import your Enum

# --- CONFIGURATION ---

# Test queries based on your provided menu data
TEST_QUERIES = [
    # --- Momo Variations ---
    {"query": "momo", "desc": "Correct, generic item"},
    {"query": "chicken momo", "desc": "Correct, specific item (Item 23)"},
    {"query": "veg momo", "desc": "Correct, specific item (Item 21)"},
    {"query": "buff momo", "desc": "Correct, specific item (Item 22)"},
    {"query": "mmoo", "desc": "Typo (fuzzy-friendly)"},
    {"query": "chiken momo", "desc": "Typo (fuzzy-friendly)"},
    {"query": "bf momo", "desc": "Abbreviation/Typo"},
    {"query": "sadheko momo", "desc": "Specific type (Item 53)"},
    {"query": "sadheko mmoo", "desc": "Specific type typo"},

    # --- Chowmein Variations ---
    {"query": "chowmein", "desc": "Correct, generic item"},
    {"query": "veg chowmein", "desc": "Correct, specific item (Item 24)"},
    {"query": "egg chowmein", "desc": "Correct, specific item (Item 26)"},
    {"query": "chicken chowmein", "desc": "Correct, specific item (Item 27)"},
    {"query": "mix chowmein", "desc": "Correct, specific item (Item 28)"},
    {"query": "chowmeen", "desc": "Typo (fuzzy-friendly)"},
    {"query": "chiken chowmein", "desc": "Typo (fuzzy-friendly)"},

    # --- Burger Variations ---
    {"query": "burger", "desc": "Correct, generic item"},
    {"query": "veg burger", "desc": "Correct, specific item (Item 29)"},
    {"query": "cheese veg burger", "desc": "Correct, specific item (Item 30)"},
    {"query": "chicken burger", "desc": "Correct, specific item (Item 31)"},
    {"query": "crunchy chicken burger", "desc": "Correct, specific item (Item 32)"},
    {"query": "burgr", "desc": "Typo (fuzzy-friendly)"},
    {"query": "chees burger", "desc": "Typo (fuzzy-friendly)"},

    # --- Pizza Variations ---
    {"query": "pizza", "desc": "Correct, generic item"},
    {"query": "chicken pizza", "desc": "Correct, specific item (Item 37)"},
    {"query": "veggie supreme", "desc": "Correct, specific item (Item 39)"},
    {"query": "meat lovers", "desc": "Correct, specific item (Item 40)"},
    {"query": "piza", "desc": "Typo (fuzzy-friendly)"},
    {"query": "spicy buff pizza", "desc": "Correct, specific item (Item 38)"},

    # --- Other Specific Items ---
    {"query": "kachila", "desc": "Correct, specific item (Item 54)"},
    {"query": "kachilla", "desc": "Typo (fuzzy-friendly)"},
    {"query": "juju dhau", "desc": "Correct, specific item (Item 47)"},
    {"query": "juju dau", "desc": "Typo (fuzzy-friendly)"},
    {"query": "brownie", "desc": "Correct, specific item (Item 46)"},
    {"query": "browne", "desc": "Typo (fuzzy-friendly)"},
    {"query": "mustang aloo", "desc": "Correct, specific item (Item 13)"},
    {"query": "mustang alo", "desc": "Typo (fuzzy-friendly)"},
    {"query": "sizzler", "desc": "Correct, generic word (Item 44)"},
    {"query": "sizler", "desc": "Typo (fuzzy-friendly)"},
    {"query": "fried rice", "desc": "Correct, common words (Items 41, 42)"},
    {"query": "fried ric", "desc": "Typo (fuzzy-friendly)"},

    # --- Queries targeting descriptions ---
    {"query": "yogurt", "desc": "Word in description (Item 47)"},
    {"query": "skewers", "desc": "Word in description (Item 36)"},
    {"query": "skewrs", "desc": "Typo in description word"},
]

# Number of times to run each query to get an average
NUM_RUNS = 5

# This must match the threshold in your router
SIMILARITY_THRESHOLD = 0.3

# --- HELPER FUNCTIONS ---

def get_query_parts(search_term: str):
    """Helper to get parts needed for FTS and Fuzzy"""
    ts_query = func.plainto_tsquery('simple', search_term)
    fts_match = Item.tsv.op('@@')(ts_query)
    fuzzy_match = func.similarity(Item.name_norm, search_term) > SIMILARITY_THRESHOLD
    return ts_query, fts_match, fuzzy_match

def test_normal_like(db: Session, search_term: str) -> int:
    """Baseline: A simple, non-indexed ILIKE search"""
    like_query = f"%{search_term}%"
    count = (
        db.query(Item)
        .filter(
            or_(
                Item.name.ilike(like_query),
                Item.description.ilike(like_query)
            )
        )
        .count()
    )
    return count

def test_fts_only(db: Session, search_term: str) -> int:
    """Mimics your FTS_ONLY mode"""
    ts_query, fts_match, _ = get_query_parts(search_term)
    count = db.query(Item).filter(fts_match).count()
    return count

def test_fuzzy_only(db: Session, search_term: str) -> int:
    """Mimics your FUZZY_ONLY mode"""
    _, _, fuzzy_match = get_query_parts(search_term)
    count = db.query(Item).filter(fuzzy_match).count()
    return count

def test_combined(db: Session, search_term: str) -> int:
    """Mimics your COMBINED mode"""
    _, fts_match, fuzzy_match = get_query_parts(search_term)
    count = db.query(Item).filter(or_(fts_match, fuzzy_match)).count()
    return count

def run_benchmark():
    """Main function to run all tests and print results"""
    
    # List of functions to test
    search_strategies = {
        "Normal ILIKE": test_normal_like,
        "FTS Only": test_fts_only,
        "Fuzzy Only": test_fuzzy_only,
        "Combined (FTS+Fuzzy)": test_combined,
    }

    db = SessionLocal()
    results = {} # To store (avg_time, result_count)

    print(f"Connecting to DB and running {NUM_RUNS} iterations for each of {len(TEST_QUERIES)} queries...")
    print("This may take a minute...")

    try:
        for strategy_name, test_func in search_strategies.items():
            print(f"Testing Strategy: {strategy_name}...")
            for test in TEST_QUERIES:
                query_str = test["query"]
                times = []
                count = 0
                
                # Warm-up run (not timed) to cache connections/etc
                test_func(db, query_str) 
                
                for i in range(NUM_RUNS):
                    start_time = time.perf_counter()
                    
                    # Run the actual query and get count
                    count = test_func(db, query_str)
                    
                    end_time = time.perf_counter()
                    times.append(end_time - start_time)
                
                avg_time = statistics.mean(times)
                key = (test["desc"], query_str)
                if key not in results:
                    results[key] = {}
                results[key][strategy_name] = (avg_time, count)

    except Exception as e:
        print(f"\n---!! AN ERROR OCCURRED !!----")
        print(f"Error: {e}")
        print("Please ensure:")
        print("1. Your .env file is correct and the SUPABASE_DB_URL is valid.")
        print("2. Your local IP is whitelisted in Supabase (if needed).")
        print("3. You ran: CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        print("4. You ran: CREATE INDEX IF NOT EXISTS idx_gin_item_name_norm ON items USING gin (name_norm gin_trgm_ops);")
        print("---------------------------------")
        return None
    finally:
        db.close()
        print("\nBenchmark complete. Database connection closed.\n")

    return results

def print_report(results):
    """Formats and prints the final report"""
    
    header = f"{'Query':<40} | {'Strategy':<22} | {'Avg. Time (ms)':<15} | {'Results Found':<10}"
    print(header)
    print("-" * len(header))

    for (desc, query), strategies in results.items():
        query_label = f"{query} ({desc})"
        
        # Sort strategies to always be in the same order
        sorted_strategies = sorted(strategies.items(), key=lambda item: list(search_strategies.keys()).index(item[0]))
        
        for strategy_name, (avg_time, count) in sorted_strategies:
            time_ms = avg_time * 1000
            print(f"{query_label:<40} | {strategy_name:<22} | {time_ms:<15.4f} | {count:<10}")
        
        print("-" * len(header))

# --- RUN SCRIPT ---
if __name__ == "__main__":
    print("Starting search benchmark...")
    report_data = run_benchmark()
    if report_data:
        print("--- Search Benchmark Results ---")
        print_report(report_data)