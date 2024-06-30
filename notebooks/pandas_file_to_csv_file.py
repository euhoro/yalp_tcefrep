import pandas as pd


# If you have multiple parquet files
import os

from notebooks.pandas_file_to_big_query import calculate_metrics

folder_path = 'raw_data/'
all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]

df = pd.concat([pd.read_parquet(f) for f in all_files])
#df = df[df['player_id'] == '6671adc2dd588a8bda035feb']
#aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days
aggregated_df = calculate_metrics(df)


aggregated_df.to_csv('output_data/out.csv')



