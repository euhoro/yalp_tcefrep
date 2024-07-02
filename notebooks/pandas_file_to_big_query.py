import pandas as pd
import os
import numpy as np

# Initialize a BigQuery client
# client = bigquery.Client()
DAY_RANK = 'day_rank'

MATCHES = 'matches'

DEPOSIT_RANK = 'deposit_rank'

TIMESTAMP_UTC = 'timestamp_utc'

COUNTRY = 'country'

DAYS_SINCE_LAST_PURCHASE = 'active_days_since_last_purchase'

DEPOSIT_AMOUNT = 'deposit_amount'

DATE = 'date'

TOURNAMENT_SCORE = 'tournament_score'

PLAYER_ID = 'player_id'

SCORE_PERC___LAST___DAYS = 'score_perc_50_last_5_days'

PERIOD_LAST_5_DAYS = 300


def calculate_metrics(df):
    df[DATE] = df['date_utc'].dt.date
    current_date = pd.Timestamp.now().date()

    # Calculate the last country
    df_sorted_country = df[df['country'].notna()].sort_values(by=['player_id', 'timestamp_utc'],
                                                              ascending=[True, False])
    last_country = df_sorted_country.drop_duplicates('player_id', keep='first').set_index('player_id')['country']

    # Calculate the average of the last 10 deposit amounts
    df_sorted_deposit = df[df['deposit_amount'].notna()].sort_values(by=['player_id', 'timestamp_utc'],
                                                                     ascending=[True, False])
    df_sorted_deposit['deposit_rank'] = df_sorted_deposit.groupby('player_id').cumcount() + 1
    avg_price_10 = df_sorted_deposit[df_sorted_deposit['deposit_rank'] <= 10].groupby('player_id')[
        'deposit_amount'].mean()

    # Calculate the weighted average of matches on last 10 active days
    matches_per_day = df[df['date'].notna()].groupby(['player_id', 'date']).size().reset_index(name='matches')
    matches_per_day_sorted = matches_per_day.sort_values(by=['player_id', 'date'], ascending=[True, False])
    matches_per_day_sorted['day_rank'] = matches_per_day_sorted.groupby('player_id').cumcount() + 1
    last_10_days = matches_per_day_sorted[matches_per_day_sorted['day_rank'] <= 10]
    last_10_days['weights'] = last_10_days.groupby('player_id')['day_rank'].transform(
        lambda x: np.arange(1, len(x) + 1))
    weighted_matches = last_10_days.groupby('player_id').apply(
        lambda x: np.average(x['matches'], weights=x['weights'])).reset_index(
        name='last_weighted_daily_matches_count_10_played_days')

    # Calculate active days since last purchase
    last_purchase_date = df[df['deposit_amount'].notna() & (df['deposit_amount'] > 0)].groupby('player_id')[
        'date'].max()
    active_days = df[df['date'].notna()].groupby('player_id')['date'].nunique()
    days_since_last_purchase = df[df['date'].notna()].groupby('player_id').apply(lambda x: pd.Series({
        'active_days_since_last_purchase': (
                    pd.date_range(start=last_purchase_date[x.name], end=current_date).difference(
                        pd.to_datetime(x['date'])).size - 1) if last_purchase_date[x.name] <= current_date else np.nan
    })).reset_index()

    # Calculate the median score over the last 5 days
    last_5_days = pd.date_range(end=current_date, periods=5).date
    scores_last_5_days = df[df['tournament_score'].notna() & df['date'].isin(last_5_days)]
    score_perc_50_last_5_days = scores_last_5_days.groupby('player_id')['tournament_score'].median().reset_index(
        name='score_perc_50_last_5_days')

    # Combine all the metrics into a single DataFrame
    aggregated_df = pd.DataFrame({
        'player_id': df['player_id'].unique()
    }).set_index('player_id')

    aggregated_df = aggregated_df.join(last_country, on='player_id')
    aggregated_df = aggregated_df.join(avg_price_10, on='player_id')
    aggregated_df = aggregated_df.join(weighted_matches.set_index('player_id'), on='player_id')
    aggregated_df = aggregated_df.join(days_since_last_purchase.set_index('player_id'), on='player_id')
    aggregated_df = aggregated_df.join(score_perc_50_last_5_days.set_index('player_id'), on='player_id')

    aggregated_df.rename(columns={"deposit_amount": "avg_price_10"}, inplace=True)
    aggregated_df = aggregated_df.reset_index()

    # Set NaN values in 'score_perc_50_last_5_days' to -1
    aggregated_df[('%s' % SCORE_PERC___LAST___DAYS)] = aggregated_df[SCORE_PERC___LAST___DAYS].fillna(-1)

    return aggregated_df


def upload_to_bigquery(df_agg):

    current_date = pd.Timestamp.now().date()
    df_agg['update_time'] = pd.Timestamp.now()
    from google.cloud import bigquery
    # Initialize a BigQuery client
    client = bigquery.Client()
    # Define BigQuery dataset and table
    dataset_id = 'your_dataset'
    table_id = 'app_user_panel'  # 'metrics_mv'#'metric_0001'
    project_id = 'yalp-tcefrep'  # Replace with your actual project ID
    # Define the destination table reference
    table_ref = client.dataset(dataset_id).table(table_id)
    # Upload the DataFrame to BigQuery
    df_agg.to_gbq(destination_table=f'{dataset_id}.{table_id}', project_id=project_id, if_exists='replace')
    print("Data uploaded to BigQuery successfully.")


if __name__ == '__main__':
    try:

        print("Data uploading ...")
        folder_path = 'raw_data/'
        all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]

        df = pd.concat([pd.read_parquet(f) for f in all_files])
        # has_values_in_column_B = df['deposit_amount'].notna().any()

        #df = df[df['player_id'] == '6671adc2dd588a8bda035feb']
        aggregated_df_all = calculate_metrics(df)

        upload_to_bigquery(aggregated_df_all)

    except Exception as e:
        print(f"Error: {e}")