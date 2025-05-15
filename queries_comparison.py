import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_CONFIG = {
    "dbname": "leetcode_uniform",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432",
}

# Path to CSV file with queries
QUERY_FILE = "/home/kseniia/Documents/data/ChatGPT_vs_Initial_queries_row_comparison.csv"

# Connect to PostgreSQL database
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Load query comparison file
df = pd.read_csv(QUERY_FILE)

# Ensure required columns exist
for col in ['ordered_equal', 'except_equal']:
    if col not in df.columns:
        df[col] = ''

def normalize_df(rows):
    """Convert query result into a normalized DataFrame with standard column names."""
    df = pd.DataFrame(rows)
    df.columns = [f"col{i}" for i in range(len(df.columns))]
    return df

def compare_as_sets(query1, query2):
    """Compare two query results as unordered sets."""
    try:
        cursor.execute(query1)
        res1 = normalize_df(cursor.fetchall())

        cursor.execute(query2)
        res2 = normalize_df(cursor.fetchall())

        if res1.shape[1] != res2.shape[1]:
            print(f"Column count mismatch: {res1.shape[1]} vs {res2.shape[1]}")
            return "COLUMN_MISMATCH"

        set1 = set(map(tuple, res1.values))
        set2 = set(map(tuple, res2.values))
        return "TRUE" if set1 == set2 else "FALSE"

    except Exception as e:
        print(f"Error comparing queries:\nQuery 1:\n{query1}\nQuery 2:\n{query2}\n{e}")
        return "ERROR"

# Main comparison loop
for idx, row in df.iterrows():
    init_query = row['Initial Query']
    opt_query = row['Optimized query']

    print(f"Comparing row {idx + 1}/{len(df)}")

    try:
        # Ordered result comparison
        cursor.execute(init_query)
        rows_init = [tuple(r.values()) for r in cursor.fetchall()]

        cursor.execute(opt_query)
        rows_opt = [tuple(r.values()) for r in cursor.fetchall()]

        ordered_equal = "TRUE" if rows_init == rows_opt else "FALSE"

        # Unordered set comparison
        except_equal = compare_as_sets(init_query, opt_query)

    except Exception as e:
        print(f"Error processing row {idx + 1}: {e}")
        ordered_equal = "ERROR"
        except_equal = "ERROR"

    # Save results
    df.at[idx, 'ordered_equal'] = ordered_equal
    df.at[idx, 'except_equal'] = except_equal

    print(f"Result: ordered = {ordered_equal}, set-based = {except_equal}")

    # Save CSV after each iteration
    df.to_csv(QUERY_FILE, index=False)

# Close DB connection
cursor.close()
conn.close()
print("Query comparison completed. Results saved to file.")
