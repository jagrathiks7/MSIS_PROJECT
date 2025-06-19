import json
import xmltodict
import pymongo
from datetime import datetime
import os


def get_data_from_source():
    choice = input("Select source type (json/xml/nosql): ").strip().lower()
    source_info = {}

    if choice == "json":
     path = input("Enter the path to the JSON file: ").strip()
     with open(path, 'r') as f:
         lines = f.readlines()
         try:
             # Try loading as a single JSON object/array
             data = json.loads(''.join(lines))
         except json.JSONDecodeError:
             # Fallback: treat each line as a separate JSON object
             data = [json.loads(line) for line in lines if line.strip()]
    
     source_info = {"source": f"local file: {path}", "type": "JSON"}

    elif choice == "xml":
        file_path = input("Enter the path to the XML file: ").strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            data = xmltodict.parse(f.read())

        # Convert XML to list of dicts if needed
        if isinstance(data, dict):
            root_key = list(data.keys())[0]
            data = data[root_key]
            if isinstance(data, dict):
                data = [data]
            elif isinstance(data, list):
                pass
            else:
                raise ValueError("Unsupported XML structure")

        source_info = {
            "source": f"Local file: {file_path}",
            "type": "XML"
        }

    elif choice == "nosql":
        try:
            # Connect to MongoDB
            client = pymongo.MongoClient("mongodb://localhost:27017/")
            print("✅ Connected to MongoDB.")

            # List databases
            dbs = client.list_database_names()
            if not dbs:
                raise Exception("No databases found in MongoDB.")
            
            print("\nAvailable Databases:")
            for i, db_name in enumerate(dbs):
                print(f"{i + 1}. {db_name}")

            db_index = int(input("Select a database by number: ")) - 1
            db_name = dbs[db_index]
            db = client[db_name]

            # List collections
            collections = db.list_collection_names()
            if not collections:
                raise Exception(f"No collections found in database '{db_name}'.")

            print(f"\nCollections in '{db_name}':")
            for i, col in enumerate(collections):
                print(f"{i + 1}. {col}")

            col_index = int(input("Select a collection by number: ")) - 1
            collection_name = collections[col_index]
            collection = db[collection_name]

            data = list(collection.find())
            if not data:
                print("⚠️  No data found in this collection.")

            source_info = {
                "source": f"MongoDB: {db_name}.{collection_name}",
                "type": "NoSQL"
            }

        except Exception as e:
            raise Exception(f"❌ MongoDB error: {e}")
    else:
        raise ValueError("Invalid input. Please choose from: json, xml, nosql")

    # Add ingestion timestamp
    source_info["timestamp"] = str(datetime.now())
    return data, source_info
