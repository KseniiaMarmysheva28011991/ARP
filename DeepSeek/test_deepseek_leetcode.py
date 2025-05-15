import requests
import pandas as pd
import re
from datetime import datetime
import time
import os

# DeepSeek API configuration
DEEPSEEK_API_KEY = ''
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Static environment information
SYSTEM = 'PostgreSQL'
VERSION = '14.17'
HOSTING_ENVIRONMENT = 'Intel(R) Core(TM) i5-6200U @ 2.3GHz, 8GB RAM, 200GB SSD, Ubuntu 22.04'
DATA_DISTRIBUTION = 'Uniform distribution, no significant skew'

LOG_FILE = 'deepseek_interactions.log'


def log_interaction(log_file, query_id, prompt, response_text):
    """Log prompt and response interactions to a file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n=== {timestamp} | Query ID: {query_id} ===\n")
        f.write(">>> Prompt Sent:\n")
        f.write(prompt + "\n")
        f.write(">>> DeepSeek Response:\n")
        f.write(response_text + "\n")
        f.write("=" * 50 + "\n")


def optimize_sql_query(original_query, db_info):
    """Send a query optimization request to DeepSeek API and return the optimized query."""
    prompt = f"""
Please rewrite the following SQL query to improve execution time.
Provide only the optimized SQL query as output, without explanations, comments, or schema modifications.

Initial Query:
{original_query}

Database Management System:
{db_info['dbms']} (Version: {db_info['version']})

Hosting Environment:
{db_info['hosting_environment']}

Tables Info:
{db_info['table_info']}

Constraints Info:
{db_info['constraint_info']}

Indexes Info:
{db_info['index_info']}

Tables Size:
{db_info['table_size']}

Data Distribution:
{db_info['data_distribution']}

Initial Execution Plan:
{db_info['execution_plan']}
"""

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 500,
        'temperature': 0.1
    }

    start_time = time.perf_counter()
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    end_time = time.perf_counter()
    duration_ms = round((end_time - start_time) * 1000, 2)

    if response.status_code == 200:
        response_data = response.json()
        response_text = response_data['choices'][0]['message']['content'].strip()
        optimized_query = re.sub(r'```sql\n?|```', '', response_text).strip()
        return prompt, optimized_query, response_text, duration_ms
    else:
        error_msg = f"Error: {response.status_code}, {response.text}"
        return prompt, None, error_msg, -1


if __name__ == '__main__':
    input_csv = 'Initial_queries_raw_results_old.csv'
    output_csv = 'optimized_queries.csv'

    df = pd.read_csv(input_csv)
    optimized_results = []

    for index, row in df.iterrows():
        print(f"Processing row {index + 1}/{len(df)}: Id={row['Id']}, TaskNo={row['TaskNo']}, ResponseId={row['ResponseId']}")

        original_query = row['Query']
        db_info = {
            'dbms': SYSTEM,
            'version': VERSION,
            'hosting_environment': HOSTING_ENVIRONMENT,
            'table_info': row.get('table_info', 'N/A'),
            'constraint_info': row.get('constraint_info', 'N/A'),
            'index_info': row.get('index_info', 'N/A'),
            'table_size': row.get('table_size', 'N/A'),
            'data_distribution': DATA_DISTRIBUTION,
            'execution_plan': row.get('explain_run_5', 'N/A')
        }

        prompt, optimized_query, response_text, duration_ms = optimize_sql_query(original_query, db_info)

        log_interaction(LOG_FILE, row['Id'], prompt, response_text if optimized_query else str(response_text))

        if optimized_query:
            optimized_results.append({
                'Id': row['Id'],
                'TaskNo': row['TaskNo'],
                'ResponseId': row['ResponseId'],
                'Difficulty': row.get('Difficulty', 'N/A'),
                'Query': optimized_query,
                'RewriteTime_ms': duration_ms
            })

    optimized_df = pd.DataFrame(optimized_results)
    optimized_df.to_csv(output_csv, index=False)

    print(f"Optimized queries saved to {output_csv}")
