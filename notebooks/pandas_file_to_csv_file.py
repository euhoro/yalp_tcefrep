import pandas as pd


# If you have multiple parquet files
import os

folder_path = 'raw_data/'
all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]

df = pd.concat([pd.read_parquet(f) for f in all_files])

aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days


aggregated_df.to_csv('output_data/out.csv')



