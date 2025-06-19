import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import json

# You may import these from your existing pipeline
from utils.transform import transformation_steps

from utils.extract import get_data_from_source

def load_to_mysql(df, table_name="cleaned_data"):
    try:
        # 1️⃣ MySQL connection string
        engine = create_engine("mysql+pymysql://root:@localhost:3306/lineage_db")

        # 2️⃣ Write DataFrame to MySQL
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        print(f"✅ Data loaded successfully into '{table_name}' table.")

    except Exception as e:
        print(f"❌ Failed to load data: {e}")

def log_metadata(source_info, transformation_steps, destination_table):
    metadata = {
        "timestamp": str(datetime.now()),
        "source": source_info,
        "transformations": transformation_steps,
        "destination": f"MySQL → {destination_table}"
    }

    # Save lineage log to a JSON file (can also push to OpenLineage/Marquez)
    with open("logs/lineage_log.json", "w") as f:
        json.dump(metadata, f, indent=4)
    print("📝 Metadata and lineage log saved to logs/lineage_log.json")

if __name__ == "__main__":
    # Optional: Get data (or receive df as input if running from ETL orchestrator)
    data, source_info = get_data_from_source()

    from transform import transform_data
    df_transformed = transform_data(data)

    # 1️⃣ Load cleaned data
    load_to_mysql(df_transformed, table_name="cleaned_data")

    # 2️⃣ Log metadata for audit/debug/lineage tracking
    log_metadata(source_info, transformation_steps, "cleaned_data")
