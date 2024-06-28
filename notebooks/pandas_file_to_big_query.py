import pandas as pd


# If you have multiple parquet files
import os

folder_path = 'raw_data/'
all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]

df = pd.concat([pd.read_parquet(f) for f in all_files])

aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days
aggregated_df.rename(columns={'tournament_score': 'metric_0001'}, inplace=True)

from google.cloud import bigquery

# Initialize a BigQuery client
client = bigquery.Client()

# # Define BigQuery dataset and table
# dataset_id = 'your_dataset'
# table_id = 'your_table'
# table_ref = client.dataset(dataset_id).table(table_id)
# aggregated_df.to_gbq(destination_table=f'{dataset_id}.{table_id}', project_id='your_project_id', if_exists='replace')

# Define BigQuery dataset and table
dataset_id = 'your_dataset'
table_id = 'metric_0001'
project_id = 'yalp-tcefrep'  # Replace with your actual project ID

# Define the destination table reference
table_ref = client.dataset(dataset_id).table(table_id)

# Upload the DataFrame to BigQuery
aggregated_df.to_gbq(destination_table=f'{dataset_id}.{table_id}', project_id=project_id, if_exists='replace')

print("Data uploaded to BigQuery successfully.")


