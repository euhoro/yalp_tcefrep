import pandas as pd
import os
import numpy as np


def calculate_metrics(df):
    df['date'] = df['date_utc'].dt.date
    

    def last_country(group):
        return group.sort_values(by='timestamp_utc').iloc[-1]['country']
    

    def avg_price_10(group):
        last_10_deposits = group.sort_values(by='timestamp_utc').tail(10)['deposit_amount']
        return last_10_deposits.mean() if not last_10_deposits.empty else np.nan
    

    def last_weighted_daily_matches_count_10_played_days(group):
        daily_matches = group.groupby('date').size()
        last_10_days = daily_matches.tail(10)
        if last_10_days.empty:
            return np.nan
        weights = np.arange(1, len(last_10_days) + 1)
        weighted_avg = (last_10_days * weights).sum() / weights.sum()
        return weighted_avg
    

    def active_days_since_last_purchase(group, current_date):
        last_purchase_date = group[group['deposit_amount'] > 0]['date'].max()
        if pd.isna(last_purchase_date):
            return np.nan
        active_days = group['date'].unique()
        days_since_last_purchase = np.setdiff1d(pd.date_range(start=last_purchase_date, end=current_date).date, active_days)
        return len(days_since_last_purchase) - 1  # subtract 1 to exclude the last purchase date itself
    

    def score_perc_50_last_5_days(group, current_date):
        last_5_days = pd.date_range(end=current_date, periods=5).date
        scores_last_5_days = group[group['date'].isin(last_5_days)]['tournament_score']
        if scores_last_5_days.empty:
            return np.nan
        return scores_last_5_days.median()

    current_date = pd.Timestamp.now().date()
    
    aggregated_df = df.groupby('player_id').apply(lambda group: pd.Series({
        'last_country': last_country(group),
        'avg_price_10': avg_price_10(group),
        'last_weighted_daily_matches_count_10_played_days': last_weighted_daily_matches_count_10_played_days(group),
        'active_days_since_last_purchase': active_days_since_last_purchase(group, current_date),
        'score_perc_50_last_5_days': score_perc_50_last_5_days(group, current_date)
    })).reset_index()


folder_path = 'raw_data/'
all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]

df = pd.concat([pd.read_parquet(f) for f in all_files])


metrics = calculate_metrics(df)
current_date = pd.Timestamp.now().date()

# Example calculations
# player_id = 12345
# print(metrics.last_country(player_id))
# print(metrics.avg_price_10(player_id))
# print(metrics.last_weighted_daily_matches_count_10_played_days(player_id))
# print(metrics.active_days_since_last_purchase(player_id, current_date))
# print(metrics.score_perc_50_last_5_days(player_id, current_date))

aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days
aggregated_df.rename(columns={'tournament_score': 'metric_0001'}, inplace=True)

aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days
aggregated_df.rename(columns={'tournament_score': 'metric_0002'}, inplace=True)

aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days
aggregated_df.rename(columns={'tournament_score': 'metric_0003'}, inplace=True)

aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days
aggregated_df.rename(columns={'tournament_score': 'metric_0004'}, inplace=True)

aggregated_df = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()#score_perc_50_last_5_days
aggregated_df.rename(columns={'tournament_score': 'metric_0005'}, inplace=True)

aggregated_df['update_time']=pd.Timestamp.now()

from google.cloud import bigquery



# # Define BigQuery dataset and table
# dataset_id = 'your_dataset'
# table_id = 'your_table'
# table_ref = client.dataset(dataset_id).table(table_id)
# aggregated_df.to_gbq(destination_table=f'{dataset_id}.{table_id}', project_id='your_project_id', if_exists='replace')


# Initialize a BigQuery client
client = bigquery.Client()

# Define BigQuery dataset and table
dataset_id = 'your_dataset'
table_id = 'metric'#'metrics_mv'#'metric_0001'
project_id = 'yalp-tcefrep'  # Replace with your actual project ID

# Define the destination table reference
table_ref = client.dataset(dataset_id).table(table_id)

# Upload the DataFrame to BigQuery
aggregated_df.to_gbq(destination_table=f'{dataset_id}.{table_id}', project_id=project_id, if_exists='replace')

print("Data uploaded to BigQuery successfully.")


