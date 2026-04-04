import pymongo
import os
import sys

def brute_force_reset():
    print("--- 1. BRUTE FORCE DROP ---")
    try:
        # Use simple PyMongo to drop the collection without any Beanie/Schema overhead
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=2000)
        db = client["realstart_db"]
        if "cities" in db.list_collection_names():
            db["cities"].drop()
            print("Successfully dropped 'cities' collection.")
        else:
            print("Collection 'cities' already gone.")
    except Exception as e:
        print(f"Brute force drop failed: {e}")

    print("\n--- 2. RE-RUNNING SEEDER ---")
    # Now that the collection and its bad indexes are gone, the seeder will work.
    os.system(f"{sys.executable} seed_all_admin.py")
    print("\n--- DONE ---")

if __name__ == "__main__":
    brute_force_reset()
