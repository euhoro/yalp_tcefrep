import pandas as pd
import os
import numpy as np
from google.cloud import bigquery, storage
from flask import Request


# Your existing function definitions (calculate_metrics and upload_to_bigquery) here
from pandas_file_to_big_query import calculate_metrics, upload_to_bigquery


def main(request: Request):
    folder_path = 'raw_data/'
    bucket_name = os.environ.get('GCP_BUCKET')

    try:
        print(f"Starting process with bucket: {bucket_name}")
        if bucket_name:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=folder_path)
            all_files = [blob.name for blob in blobs if blob.name.endswith('.parquet')]

            data_frames = []
            for file in all_files:
                blob = bucket.blob(file)
                temp_file = f'/tmp/{os.path.basename(file)}'
                blob.download_to_filename(temp_file)
                data_frames.append(pd.read_parquet(temp_file))

            df = pd.concat(data_frames)
        else:
            # Working with local folder
            all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]
            df = pd.concat([pd.read_parquet(f) for f in all_files])

        aggregated_df_all = calculate_metrics(df)
        upload_to_bigquery(aggregated_df_all)
        return 'Data uploaded successfully.'
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}", 500