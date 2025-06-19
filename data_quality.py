import datetime
import re
import mysql.connector
import pandas as pd


# ------------------------------------------------------------------------------
# 1️⃣ Select dataset format
# ------------------------------------------------------------------------------
print("Select your dataset format:")
print("1. CSV")
print("2. MySQL")
choice = int(input("Enter 1 or 2: ").strip())    

# ------------------------------------------------------------------------------
# 2️⃣ Loading the dataset
# ------------------------------------------------------------------------------
if choice == 1:
    # CSV
    file_name = input("Enter CSV file path: ").strip()
    df = pd.read_csv(file_name)
    print("Loaded CSV successfully.")
elif choice == 2:
    # 1️⃣ Connect to MySQL
 
    # MySQL
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sample'
    )
    print("Database connected successfully")

    print("\nHow would you like to retrieve data from MySQL?")
    print("1. Enter custom query")
    print("2. Select table by name")
    load_option = int(input().strip())    

    if load_option == 1:
        # Custom query
        query = input("Enter your MySQL query to fetch data: ").strip()
        df = pd.read_sql(query, db)
        print("Data retrieved successfully")

    elif load_option == 2:
        # List tables first
        cursor = db.cursor()
        cursor.execute("SHOW TABLES")
        tables = [item[0] for item in cursor.fetchall()]
        print("\nAvailable tables:")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table}")

        table_idx = int(input("Select table by number: ").strip()) - 1
        table_name = tables[table_idx]

        df = pd.read_sql(f"SELECT * FROM {table_name}", db)
        print(f"Table {table_name} retrieved successfully")

    db.close()
    


# ------------------------------------------------------------------------------
# 4️⃣ Calculate data quality metrics
# ------------------------------------------------------------------------------
# Per-column completeness (% of non-null values)
print("\n--- Completeness Report (per column) ---")
column_completeness = df.notnull().mean() * 100

for col, completeness_val in column_completeness.items():
    print(f"{col}: {completeness_val:.2f}% complete")

# Average completeness across all columns
average_completeness = column_completeness.mean()
print(f"\nOverall Average Completeness: {average_completeness:.2f}%")

 
# Uniqueness (with composite key picker)
if df.empty or df.index.empty:
    uniqueeness = 0
else:
    print("\nSelect column(s) to compute uniqueness (comma-separated by number):")
    for i, col in enumerate(df.columns, start=1):
        print(f"{i}. {col}")

    col_indices_input = input("Enter column numbers (comma-separated): ").strip()
    col_indices = [int(i) - 1 for i in col_indices_input.split(",") if i.strip().isdigit()]
    composite_key = [df.columns[i] for i in col_indices]

    # Calculate number of unique combinations
    num_unique = df.groupby(composite_key).ngroups

    # Calculate uniqueness percentage
    uniqueeness = (num_unique / len(df)) * 100

    print(f"Using composite key: {composite_key} for uniqueness.")
    print(f"Number of unique combinations: {num_unique} out of {len(df)}")
    print(f"Uniqueeness: {uniqueeness:.2f}%")



# Consistency (duplicate rows)
consistency = (1 - (df.duplicated().sum() / len(df))) * 100
# Apply multiple validation checks
print("\nHow many validation checks do you want to apply?")
num_checks = int(input("Enter number of checks: ").strip())    

# Store validation results for each check
validation_pass_rates = []

for _ in range(num_checks):
    print("\nSelect column to validate:")
    for i, col in enumerate(df.columns, start=1):
        print(f"{i}. {col}")

    col_choice = int(input("Enter column number: ").strip()) - 1
    selected_col = df.columns[col_choice]

    print("Choose validation method:")
    print("1. List of acceptable values")
    print("2. Range Check")
    print("3. Pattern (Regular Expression)")

    validation_option = int(input("Enter your choice (1-3): ").strip())    

    if validation_option == 1:
        # List of acceptable values
        print("Enter the list of acceptable values (comma-separated):")
        acceptable_vals = input("Enter values: ").strip().split(',')

        acceptable_vals = [val.strip() for val in acceptable_vals]

        valid_indices = [x in acceptable_vals for x in df[selected_col]]

    elif validation_option == 2:
        # Range Check
        minimum = float(input("Enter minimum range: ").strip()) 
        maximum = float(input("Enter maximum range: ").strip()) 
        valid_indices = [minimum <= x <= maximum for x in df[selected_col]]

    elif validation_option == 3:
        # Pattern Check
        pattern = input(r"Enter a pattern (regular expression): ").strip()
        valid_indices = [bool(re.match(pattern, str(x))) for x in df[selected_col]]

    else:
        print("Invalid option.")
        continue

    # Count valid and compute accuracy for this check
    valid_count = sum(valid_indices)
    total = len(valid_indices)
    accuracy = (valid_count / total) * 100


    print(f"Validation for column {selected_col}:")
    print(f"Valid Count: {valid_count}")
    print(f"Total Count: {total}")
    print(f"Accuracy: {accuracy:.2f}%")

    validation_pass_rates.append(accuracy)


# Average accuracy across all checks
average_accuracy = sum(validation_pass_rates) / len(validation_pass_rates)
print(f"Average Accuracy across all checks: {average_accuracy:.2f}%")






# Duplicate rate
duplicate_count = df.duplicated().sum()
duplicate_rate = (duplicate_count / len(df)) * 100


# Overall data quality score
metrics = [average_completeness, uniqueeness, consistency, average_accuracy]
data_quality_score = sum(metrics) / len(metrics)


# ------------------------------------------------------------------------------
# 5️⃣ Prints results
# ------------------------------------------------------------------------------
print("\n--- Data Quality Report ---")
print(f"Completion: {average_completeness:.2f}%")
print(f"Uniqueeness: {uniqueeness:.2f}%")
print(f"Consistency: {consistency:.2f}%")
print(f"Accuracy: {average_accuracy:.2f}%")


print(f"Duplicate Rate: {duplicate_rate:.2f}%")
print(f"Overall Data Quality Score: {data_quality_score:.2f}%")
print("----------------------------")
