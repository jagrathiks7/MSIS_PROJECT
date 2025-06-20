import pandas as pd
import json
import os
import re
import xml.etree.ElementTree as ET
from pandas import json_normalize

# -------------------------------------------------------------------------
# 1️⃣ Choose input type: JSON or XML
# -------------------------------------------------------------------------
print("Select input format:")
print("1. JSON or NDJSON")
print("2. XML")
format_choice = input("Enter 1 or 2: ").strip()

file_path = input("Enter full path to your file: ").strip().strip('"')

if not os.path.isfile(file_path):
    print("❌ File not found. Exiting.")
    exit()

# -------------------------------------------------------------------------
# 2️⃣ Load JSON / NDJSON / XML and convert to DataFrame
# -------------------------------------------------------------------------
if format_choice == '1':  # JSON or NDJSON
    try:
        # Try NDJSON
        df = pd.read_json(file_path, lines=True)
        print("✅ NDJSON (line-delimited JSON) loaded successfully.")
    except ValueError:
        try:
            # Fallback to regular JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            df = pd.json_normalize(json_data)
            print("✅ Regular JSON loaded and flattened successfully.")
        except Exception as e:
            print(f"❌ Failed to parse JSON: {e}")
            exit()

elif format_choice == '2':  # XML
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        records = []
        for child in root:
            record = {}
            for element in child.iter():
                tag = element.tag
                text = element.text.strip() if element.text else ""
                if tag != child.tag:
                    record[tag] = text
            if record:
                records.append(record)

        df = pd.DataFrame(records)
        print("✅ XML parsed and loaded into DataFrame.")
    except Exception as e:
        print(f"❌ Failed to parse XML: {e}")
        exit()

else:
    print("❌ Invalid format choice.")
    exit()

# -------------------------------------------------------------------------
# 3️⃣ Data Quality Checks
# -------------------------------------------------------------------------

# Completeness
print("\n--- Completeness Report ---")
column_completeness = df.notnull().mean() * 100
for col, val in column_completeness.items():
    print(f"{col}: {val:.2f}% complete")
average_completeness = column_completeness.mean()

# Uniqueness
if df.empty or df.index.empty:
    uniqueness = 0
else:
    print("\nSelect column(s) for uniqueness (comma-separated numbers):")
    for i, col in enumerate(df.columns, start=1):
        print(f"{i}. {col}")
    col_indices_input = input("Enter column numbers: ").strip()
    col_indices = [int(i) - 1 for i in col_indices_input.split(",") if i.strip().isdigit()]
    composite_key = [df.columns[i] for i in col_indices]
    num_unique = df.groupby(composite_key).ngroups
    uniqueness = (num_unique / len(df)) * 100
    print(f"Composite key: {composite_key}")
    print(f"Unique rows: {num_unique} / {len(df)}")
    print(f"Uniqueness: {uniqueness:.2f}%")

# Consistency (duplicate detection)
duplicate_count = df.duplicated().sum()
consistency = (1 - (duplicate_count / len(df))) * 100

# Accuracy checks
print("\nHow many validation checks would you like to perform?")
num_checks = int(input("Enter number of checks: ").strip())
validation_pass_rates = []

for _ in range(num_checks):
    print("\nSelect column to validate:")
    for i, col in enumerate(df.columns, start=1):
        print(f"{i}. {col}")
    col_choice = int(input("Enter column number: ").strip()) - 1
    selected_col = df.columns[col_choice]

    print("Choose validation type:")
    print("1. List of acceptable values")
    print("2. Range Check (numerical)")
    print("3. Pattern Match (Regex)")
    method = int(input("Enter 1, 2, or 3: ").strip())

    if method == 1:
        values = input("Enter acceptable values (comma-separated): ").split(",")
        values = [v.strip() for v in values]
        valid_indices = [str(x).strip() in values for x in df[selected_col]]

    elif method == 2:
        min_val = float(input("Enter minimum value: "))
        max_val = float(input("Enter maximum value: "))
        valid_indices = [min_val <= float(x) <= max_val if str(x).replace('.', '', 1).isdigit() else False for x in df[selected_col]]

    elif method == 3:
        pattern = input("Enter regex pattern: ").strip()
        valid_indices = [bool(re.match(pattern, str(x))) for x in df[selected_col]]

    else:
        print("❌ Invalid option. Skipping check.")
        continue

    valid_count = sum(valid_indices)
    accuracy = (valid_count / len(valid_indices)) * 100
    validation_pass_rates.append(accuracy)
    print(f"✔ Accuracy for '{selected_col}': {accuracy:.2f}%")

average_accuracy = sum(validation_pass_rates) / len(validation_pass_rates) if validation_pass_rates else 0

# -------------------------------------------------------------------------
# 4️⃣ Final Report
# -------------------------------------------------------------------------
metrics = [average_completeness, uniqueness, consistency, average_accuracy]
data_quality_score = sum(metrics) / len(metrics)

print("\n--- Final Data Quality Report ---")
print(f"Completeness: {average_completeness:.2f}%")
print(f"Uniqueness: {uniqueness:.2f}%")
print(f"Consistency: {consistency:.2f}%")
print(f"Accuracy: {average_accuracy:.2f}%")
print(f"Duplicate Rate: {(duplicate_count / len(df)) * 100:.2f}%")
print(f"Overall Data Quality Score: {data_quality_score:.2f}%")
print("--------------------------------------------------")
