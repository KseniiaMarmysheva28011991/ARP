import os
import sys
import csv
import time
import json
import argparse
import jsonlines
import jpype

# Add parent directory to the path for internal module imports
sys.path.append('..')

# Import project modules
from my_rewriter.config import init_db_config
from my_rewriter.database import DBArgs, Database
from my_rewriter.rewrite import learned_rewrite

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Run Learned Rewrite for SQL query optimization")
parser.add_argument('--database', type=str, required=True, help='Target PostgreSQL database name')
parser.add_argument('--logdir', type=str, default='logs_learned_rewrite', help='Directory to store logs/results')
parser.add_argument('--large', action='store_true', help='Flag to indicate use of a large database')
args = parser.parse_args()

# Initialization
BUDGET = 20  # Rewrite budget (e.g., max number of transformations)
DATABASE = args.database

# Load PostgreSQL config and initialize DBArgs
pg_config = init_db_config(DATABASE)
pg_args = DBArgs(pg_config)

# Define log/result file path
log_file_path = os.path.join(args.logdir, DATABASE, 'res.jsonl')
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Load processed query names to avoid re-processing
history = set()
if os.path.exists(log_file_path):
    with open(log_file_path, 'r') as fin:
        for line in fin:
            obj = json.loads(line)
            history.add(obj['name'])

# Prepare result log for appending
out_file = jsonlines.open(log_file_path, "a")
out_file._flush = True  # Ensure immediate disk writing

# Set dataset name and load schema
if 'leetcode_uniform' in DATABASE:
    DATASET = 'leetcode_uniform'
else:
    raise ValueError(f"Unsupported dataset in database name: {DATABASE}")

schema_path = os.path.join('..', DATASET, 'create_tables.sql')
with open(schema_path, 'r') as f:
    schema = f.read()

# Rewrite function
def my_rewrite(query: str, schema: str, name: str) -> dict:
    """Apply learned rewrite to a SQL query and return metadata."""
    out_dict = {'name': name}
    create_tables = [stmt for stmt in schema.split(';') if stmt.strip()]
    start = time.time()
    try:
        # Call the learned_rewrite function
        res = learned_rewrite(
            query, create_tables, BUDGET,
            host=pg_config.get('host', 'localhost'),
            port=str(pg_config.get('port', 5432)),
            user=pg_config.get('user', 'postgres'),
            password=pg_config.get('password', 'postgres'),
            dbname=pg_config.get('dbname', 'postgres')
        )
        print(f"Query '{name}' rewritten successfully.")

        # Extract results
        out_dict['input_sql'] = res.get("input_sql", query)
        out_dict['input_cost'] = float(res.get("input_cost", -1))
        out_dict['output_sql'] = res.get("output_sql", 'None')
        out_dict['output_cost'] = float(res.get("output_cost", -1))
        out_dict['used_rules'] = [str(r) for r in res.get("used_rules", [])]
        out_dict['rewrite_time'] = int(res.get("time", (time.time() - start) * 1000))
    except jpype.JException as e:
        print(f"[ERROR] Failed to rewrite query '{name}': {e}")
        out_dict['input_sql'] = query
        db = Database(pg_args)
        out_dict['input_cost'] = db.cost_estimation(query)
        out_dict['output_sql'] = 'None'
        out_dict['output_cost'] = -1
        out_dict['used_rules'] = []
        out_dict['rewrite_time'] = int((time.time() - start) * 1000)
    return out_dict

# Main execution: process LeetCode queries
if DATASET == 'leetcode_uniform':
    queries_path = os.path.join('..', DATASET, f'{DATASET}.csv')
    print(f"Reading input queries from: {queries_path}")
    
    with open(queries_path, mode='r') as fin:
        reader = csv.DictReader(fin)

        # Prepare output CSV for optimized queries
        output_csv_path = os.path.join(args.logdir, DATABASE, 'optimized_queries_leetcode_lr.csv')
        with open(output_csv_path, mode='w', newline='') as csvfile:
            fieldnames = reader.fieldnames + ['Optimized Query', 'Input Cost', 'Output Cost', 'Used Rules', 'Rewrite Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Process each query
            for row in reader:
                query = row['Query']
                name = row.get('Name', 'unknown')

                # Skip if already processed
                if name in history:
                    continue

                # Run learned rewrite
                out_dict = my_rewrite(query, schema, name)

                # Populate result fields
                row['Optimized Query'] = out_dict['output_sql'] if out_dict['output_sql'] != 'None' else 'error'
                row['Input Cost'] = out_dict['input_cost']
                row['Output Cost'] = out_dict['output_cost']
                row['Used Rules'] = ', '.join(out_dict['used_rules'])
                row['Rewrite Time'] = out_dict['rewrite_time']

                # Write to output files
                writer.writerow(row)
                out_file.write(out_dict)