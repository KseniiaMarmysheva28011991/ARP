import os
import sys
import csv
import argparse

# Add parent directory to the Python path for module imports
sys.path.append('..')

# Import project modules
from my_rewriter.config import init_llms, init_db_config
from my_rewriter.database import DBArgs, Database
from my_rewriter.test_utils import test
from my_rewriter.rag_retrieve import init_docstore

# Argument Parsing 
parser = argparse.ArgumentParser(description="Run R-Bot rewrite for SQL queries using retrieval-augmented generation.")
parser.add_argument('--database', type=str, required=True, help='Target PostgreSQL database name')
parser.add_argument('--logdir', type=str, default='logs', help='Directory to store logs/results')
parser.add_argument('--index', type=str, default='hybrid', help='Index type used for retrieval')
parser.add_argument('--topk', type=int, default=10, help='Top-k documents to retrieve')
args = parser.parse_args()

# Configuration and Constants 
model_args = init_llms(args.logdir)
pg_config = init_db_config(args.database)
pg_args = DBArgs(pg_config)

RETRIEVER_TOP_K = args.topk
CASE_BATCH = 5
RULE_BATCH = 10
REWRITE_ROUNDS = 1
DATABASE = args.database

# Infer dataset type from database name
if 'leetcode_uniform' in DATABASE:
    DATASET = 'leetcode_uniform'
else:
    raise ValueError(f"Unsupported dataset: {DATABASE}")

LOG_DIR = os.path.join(args.logdir, DATASET)
os.makedirs(LOG_DIR, exist_ok=True)

# Load schema
schema_path = os.path.join('..', DATASET, 'create_tables.sql')
with open(schema_path, 'r') as f:
    schema = f.read()

# Initialize document store for RAG
docstore = init_docstore()

# Main Execution
if DATASET == 'leetcode_uniform':
    queries_path = os.path.join('..', DATASET, f'{DATASET}.csv')
    print(f"Reading input queries from: {queries_path}")

    with open(queries_path, mode='r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)

        output_csv_path = os.path.join(args.logdir, DATABASE, 'optimized_queries_leetcode_rbot.csv')
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = reader.fieldnames + ['Optimized Query', 'Input Cost', 'Output Cost', 'Used Rules', 'Rewrite Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                query = row['Query']  
                name = row.get('Id', 'unknown')

                print(f"Processing query ID: {name}")

                # Perform rewrite with R-Bot
                test(
                    name, query, schema, pg_args, model_args, docstore, LOG_DIR,
                    RETRIEVER_TOP_K=RETRIEVER_TOP_K, CASE_BATCH=CASE_BATCH,
                    RULE_BATCH=RULE_BATCH, REWRITE_ROUNDS=REWRITE_ROUNDS, index=args.index
                )

                # Read the rewrite result from the log file
                log_filename = os.path.join(LOG_DIR, f"{name}.log")
                if not os.path.exists(log_filename):
                    print(f"Log file not found: {log_filename}")
                    continue

                last_res_line = None
                with open(log_filename, 'r') as f:
                    for line in f:
                        if 'root INFO Rewrite Execution Results' in line:
                            last_res_line = line

                if last_res_line:
                    try:
                        # Parse result from log line (assumes result is in a Python dict format)
                        res = eval(last_res_line[last_res_line.find('{'):])
                        row['Optimized Query'] = res.get('output_sql', 'error')
                        row['Output Cost'] = res.get('output_cost', '')
                        row['Used Rules'] = ', '.join(res.get('used_rules', []))
                        row['Rewrite Time'] = res.get('time', '')

                        if row['Optimized Query'] == 'None':
                            row['Optimized Query'] = 'error'

                        writer.writerow(row)

                    except Exception as e:
                        print(f"Error parsing result for ID {name}: {e}")
                        continue
                else:
                    print(f"No rewrite result found for ID {name}. Skipping.")
                    continue