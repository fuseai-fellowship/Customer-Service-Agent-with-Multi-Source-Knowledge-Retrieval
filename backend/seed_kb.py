import os
import sys

# Ensure the app modules can be imported
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.models import KnowledgeBase
from app.core.embedding import get_embedding_model
from sqlalchemy import text

# The data provided in the specific order
KB_DATA = [
    {
        "id": 1,
        "topic": "Basic Info",
        "content": "Lumina Bistro is located at Jhamsikhel, Lalitpur, Kathmandu. It operates Monday–Friday from 11:00 AM to 10:00 PM, and Saturday–Sunday from 10:00 AM to 11:00 PM. Reservations can be made via phone at +977-01-5551234 or through the website www.luminabistro.com. The restaurant offers indoor and outdoor seating, complimentary Wi-Fi, and accepts all major credit cards as well as mobile payments such as eSewa and Khalti."
    },
    {
        "id": 2,
        "topic": "Story & Concept",
        "content": "Founded in 2018 by chef Anil Shrestha, Lumina Bistro brings a modern, relaxed dining experience to Kathmandu. The restaurant emphasizes locally sourced ingredients and sustainable practices. The interior combines warm wooden accents, soft lighting, and contemporary décor, creating a welcoming environment. A garden terrace allows guests to enjoy meals outdoors, surrounded by lush greenery and views of the valley."
    },
    {
        "id": 3,
        "topic": "Services & Amenities",
        "content": "Lumina Bistro provides both indoor and outdoor seating, including a private dining room suitable for group events or business meetings. Complimentary Wi-Fi and power outlets are available for guests. Outdoor areas are pet-friendly, and high chairs are provided for children. The restaurant hosts live music sessions on Fridays and organizes special cultural evenings during major Nepalese festivals. Takeout and delivery services are offered through local apps like Foodmandu and Pathao Eats."
    },
    {
        "id": 4,
        "topic": "Accessibility & Directions",
        "content": "Lumina Bistro is wheelchair accessible, with ramps and accessible restrooms. Free parking is available on-site, and additional street parking is nearby. The restaurant is a 10-minute walk from the Lalitpur Bus Park and can be easily reached via taxi or public microbuses. Signage guides visitors to both the indoor dining areas and the garden terrace."
    },
    {
        "id": 5,
        "topic": "Safety & Policies",
        "content": "Lumina Bistro maintains high standards of hygiene, including daily sanitization of tables, menus, and high-touch areas. Staff wear face masks during peak hours, and guests are encouraged to follow standard safety protocols. Allergy information is available upon request, and the kitchen follows strict cross-contamination prevention procedures. Refund and cancellation policies for reservations and group bookings are clearly outlined on the restaurant’s website."
    },
    {
        "id": 6,
        "topic": "Events & Community",
        "content": "Lumina Bistro organizes cultural evenings, live music nights, and seasonal workshops. The restaurant collaborates with local farms to source fresh ingredients and actively participates in community initiatives such as tree planting and charity drives. Festival specials for events like Dashain, Tihar, and Holi are promoted on the restaurant’s website and social media platforms."
    },
    {
        "id": 7,
        "topic": "Media & Marketing",
        "content": "Lumina Bistro has been featured in Nepali lifestyle magazines and local food blogs for its contemporary décor, sustainable approach, and community engagement. Recent campaigns include “Summer Garden Evenings” and “Holi Festival Specials,” promoted via Instagram, Facebook, and email newsletters. Official photos of the garden terrace, events, and ambiance are available for marketing purposes."
    }
]

def seed_data():
    db = SessionLocal()
    print("Loading embedding model...")
    model = get_embedding_model()

    print(f"Found {len(KB_DATA)} topics to seed.")

    try:
        # Clear table and reset sequence to ensure clean IDs
        print("Cleaning existing Knowledge Base data...")
        db.execute(text("TRUNCATE TABLE knowledge_base RESTART IDENTITY;"))
        db.commit()

        new_count = 0
        
        for item in KB_DATA:
            print(f"  • Processing ID {item['id']}: '{item['topic']}'")
            
            # Generate embedding
            emb = model.encode(item["content"]).tolist()
            
            # Create DB object with EXPLICIT ID
            kb_item = KnowledgeBase(
                id=item["id"],
                topic=item["topic"],
                content=item["content"],
                emb=emb
            )
            db.add(kb_item)
            new_count += 1
        
        db.commit()
        
        # Reset the primary key sequence to start after the highest ID we inserted
        # This ensures any NEW items created via the frontend won't conflict (e.g., next ID will be 8)
        max_id = KB_DATA[-1]["id"]
        db.execute(text(f"SELECT setval('knowledge_base_id_seq', {max_id}, true);"))
        db.commit()
        
        print(f"\n✅ Success! Added {new_count} items with correct IDs.")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()