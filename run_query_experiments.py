import psycopg2
import pandas as pd
import statistics

# === Database connection parameters ===
DB_CONFIG = {
    "dbname": "leetcode_uniform",
    "user": "postgres",
    "password": "", 
    "host": "localhost",
    "port": "5432",
}

N_RUNS = 5  # Number of executions per query
QUERY_FILE = "/home/kseniia/Documents/data/Initial_queries_raw_results.csv"  # Input CSV file with queries

# === Resets PostgreSQL configuration and statistics to reduce caching effects before each run.
def reset_cache():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute("RESET ALL;")
                cursor.execute("SELECT pg_stat_reset();")
    except psycopg2.Error as e:
        print(f"Cache reset error: {e}")

# === Executes a SQL query using EXPLAIN ANALYZE and extracts execution time, cost, rows, and full plan. ===
def execute_query(query, conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET max_parallel_workers_per_gather = 0;")
            cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS, TIMING OFF) {query}")
            explain_result = cursor.fetchall()

        explain_text = "\n".join([line[0] for line in explain_result])

        exec_line = next((l[0] for l in explain_result if "Execution Time" in l[0]), None)
        exec_time = float(exec_line.split(":")[1].strip().split(" ")[0]) if exec_line else None

        cost_line = next((l[0] for l in explain_result if "cost=" in l[0]), None)
        cost = float(cost_line.split("cost=")[1].split("..")[1].split(" ")[0]) if cost_line else None

        rows_line = next((l[0] for l in explain_result if "actual rows=" in l[0]), None)
        row_count = int(rows_line.split("actual rows=")[1].split(" ")[0]) if rows_line else None

        return exec_time, cost, row_count, explain_text

    except Exception as e:
        print(f"[execute_query ERROR] {e}")
        conn.rollback()
        return None, None, None, None

# === Main function that runs each query N times, collects performance stats, and saves results to CSV. ===
def run_experiments():
    df = pd.read_csv(QUERY_FILE)

    for i in range(1, N_RUNS + 1):
        df[f"time_pg_{i}"] = None
        df[f"cost_{i}"] = None
        df[f"rows_{i}"] = None
        df[f"explain_run_{i}"] = None

    result_columns = [
        "avg_pg_time", "median_pg_time", "p75_pg_time", "p90_pg_time",
        "avg_cost", "median_cost",
        "avg_rows", "median_rows", "p75_rows", "p90_rows"
    ]
    for col in result_columns:
        if col not in df.columns:
            df[col] = None

    with psycopg2.connect(**DB_CONFIG) as conn:
        for index, row in df.iterrows():
            query = row["Query"].strip()
            if not query:
                continue

            pg_times = []
            costs = []
            row_counts = []
            explain_text_final = None

            # Warm-up run to pre-load data
            print(f"\n[INFO] Warming up query before measurement...")
            reset_cache()
            _ = execute_query(query, conn)

            for run in range(1, N_RUNS + 1):
                reset_cache()
                pg_time, cost, row_count, explain_text = execute_query(query, conn)

                if pg_time is None:
                    df.at[index, f"time_pg_{run}"] = "error"
                    df.at[index, f"cost_{run}"] = "error"
                    df.at[index, f"rows_{run}"] = "error"
                    df.at[index, f"explain_run_{run}"] = "error"
                    continue

                df.at[index, f"time_pg_{run}"] = pg_time
                df.at[index, f"cost_{run}"] = cost
                df.at[index, f"rows_{run}"] = row_count
                df.at[index, f"explain_run_{run}"] = explain_text

                pg_times.append(pg_time)
                costs.append(cost)
                row_counts.append(row_count)

                print(f"\n[Task {row.get('TaskNo', 'N/A')} | Response {row.get('ResponseId', 'N/A')}]")
                print(f"[RUN {run}/{N_RUNS}]")
                print(f"   - Execution Time: {pg_time:.4f} ms")
                print(f"   - Query Cost:     {cost}")
                print(f"   - Rows Returned:  {row_count}")

            # Aggregating results
            if pg_times:
                df.at[index, "avg_pg_time"] = statistics.mean(pg_times)
                df.at[index, "median_pg_time"] = statistics.median(pg_times)
                df.at[index, "p75_pg_time"] = statistics.quantiles(pg_times, n=4)[2]
                df.at[index, "p90_pg_time"] = statistics.quantiles(pg_times, n=10)[8]
            else:
                for col in ["avg_pg_time", "median_pg_time", "p75_pg_time", "p90_pg_time"]:
                    df.at[index, col] = "error"

            if costs and "error" not in costs:
                df.at[index, "avg_cost"] = statistics.mean(costs)
                df.at[index, "median_cost"] = statistics.median(costs)
            else:
                df.at[index, "avg_cost"] = "error"
                df.at[index, "median_cost"] = "error"

            if row_counts:
                df.at[index, "avg_rows"] = statistics.mean(row_counts)
                df.at[index, "median_rows"] = statistics.median(row_counts)
                df.at[index, "p75_rows"] = statistics.quantiles(row_counts, n=4)[2]
                df.at[index, "p90_rows"] = statistics.quantiles(row_counts, n=10)[8]
            else:
                for col in ["avg_rows", "median_rows", "p75_rows", "p90_rows"]:
                    df.at[index, col] = "error"

            # Save after each row for reliability
            df.to_csv(QUERY_FILE, index=False)

    print(f"\nAll experiments completed. Results saved to {QUERY_FILE}")

if __name__ == "__main__":
    run_experiments()
