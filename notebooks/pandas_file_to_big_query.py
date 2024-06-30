import pandas as pd
import os
import numpy as np

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
    df[DATE] = df[('%s_utc' % DATE)].dt.date
    current_date = pd.Timestamp.now().date()

    # Calculate the last country
    df_sorted_country = df[df[('%s' % COUNTRY)].notna()].sort_values(by=[PLAYER_ID, ('%s' % TIMESTAMP_UTC)],
                                                                     ascending=[True, False])
    last_country = df_sorted_country.drop_duplicates(PLAYER_ID, keep='first').set_index(PLAYER_ID)[COUNTRY]

    # Calculate the average of the last 10 deposit amounts
    df_sorted_deposit = df[df[DEPOSIT_AMOUNT].notna()].sort_values(by=[PLAYER_ID, TIMESTAMP_UTC],
                                                                   ascending=[True, False])
    df_sorted_deposit[('%s' % DEPOSIT_RANK)] = df_sorted_deposit.groupby(PLAYER_ID).cumcount() + 1
    avg_price_10 = df_sorted_deposit[df_sorted_deposit[DEPOSIT_RANK] <= 10].groupby(PLAYER_ID)[
        DEPOSIT_AMOUNT].mean()

    # Calculate the weighted average of matches on last 10 active days
    matches_per_day = df[df[DATE].notna()].groupby([PLAYER_ID, DATE]).size().reset_index(name=('%s' % MATCHES))
    matches_per_day_sorted = matches_per_day.sort_values(by=[PLAYER_ID, DATE], ascending=[True, False])
    matches_per_day_sorted[('%s' % DAY_RANK)] = matches_per_day_sorted.groupby(PLAYER_ID).cumcount() + 1
    last_10_days = matches_per_day_sorted[matches_per_day_sorted[DAY_RANK] <= 10]
    last_10_days['weights'] = last_10_days.groupby(PLAYER_ID)[DAY_RANK].transform(
        lambda x: np.arange(1, len(x) + 1))
    weighted_matches = last_10_days.groupby(PLAYER_ID).apply(
        lambda x: np.average(x[MATCHES], weights=x['weights'])).reset_index(
        name=('last_weighted_daily_%s_count_10_played_days' % MATCHES))

    # Calculate active days since last purchase
    last_purchase_date = df[df[('%s' % DEPOSIT_AMOUNT)].notna() & (df[DEPOSIT_AMOUNT] > 0)].groupby(PLAYER_ID)[
        DATE].max()
    active_days = df[df[DATE].notna()].groupby(PLAYER_ID)[DATE].nunique()
    days_since_last_purchase = df[df[DATE].notna()].groupby(PLAYER_ID).apply(lambda x: pd.Series({
        ('%s' % DAYS_SINCE_LAST_PURCHASE): (
                pd.date_range(start=last_purchase_date[x.name], end=current_date).difference(
                        pd.to_datetime(x[DATE])).size - 1) if last_purchase_date[x.name] <= current_date else np.nan
    })).reset_index()

    # Calculate the median score over the last 5 days
    last_5_days = pd.date_range(end=current_date, periods=PERIOD_LAST_5_DAYS).date
    scores_last_5_days = df[df[('%s' % TOURNAMENT_SCORE)].notna() & df[('%s' % DATE)].isin(last_5_days)]
    score_perc_50_last_5_days = scores_last_5_days.groupby(PLAYER_ID)[TOURNAMENT_SCORE].median().reset_index(
        name=SCORE_PERC___LAST___DAYS)

    # Combine all the metrics into a single DataFrame
    aggregated_df = pd.DataFrame({
        PLAYER_ID: df[PLAYER_ID].unique()
    }).set_index(PLAYER_ID)

    aggregated_df = aggregated_df.join(last_country, on=PLAYER_ID)
    aggregated_df = aggregated_df.join(avg_price_10, on=PLAYER_ID)
    aggregated_df = aggregated_df.join(weighted_matches.set_index(PLAYER_ID), on=PLAYER_ID)
    aggregated_df = aggregated_df.join(days_since_last_purchase.set_index(PLAYER_ID), on=PLAYER_ID)
    aggregated_df = aggregated_df.join(score_perc_50_last_5_days.set_index('%s' % PLAYER_ID), on=PLAYER_ID)

    aggregated_df = aggregated_df.reset_index()

    # Set NaN values in 'score_perc_50_last_5_days' to -1
    aggregated_df[('%s' % SCORE_PERC___LAST___DAYS)] = aggregated_df[SCORE_PERC___LAST___DAYS].fillna(-1)

    return aggregated_df

folder_path = 'raw_data/'
all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]

df = pd.concat([pd.read_parquet(f) for f in all_files])
#has_values_in_column_B = df['deposit_amount'].notna().any()


#df = df[df['player_id'] == '6671adc2dd588a8bda035feb']
aggregated_df_all = calculate_metrics(df)

current_date = pd.Timestamp.now().date()
# missing_values = aggregated_df_all.isnull().any()
# columns_with_missing_values = missing_values[missing_values].index.tolist()
# print("Columns with missing values:", columns_with_missing_values)
# aggregated_df2.rename(columns={'tournament_score': 'metric_0001'}, inplace=True)
#
# aggregated_df2 = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()  # score_perc_50_last_5_days
# aggregated_df2.rename(columns={'tournament_score': 'metric_0002'}, inplace=True)
#
# aggregated_df2 = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()  # score_perc_50_last_5_days
# aggregated_df2.rename(columns={'tournament_score': 'metric_0003'}, inplace=True)
#
# aggregated_df2 = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()  # score_perc_50_last_5_days
# aggregated_df2.rename(columns={'tournament_score': 'metric_0004'}, inplace=True)
#
# aggregated_df2 = df.groupby('player_id').agg({'tournament_score': 'sum'}).reset_index()  # score_perc_50_last_5_days
# aggregated_df2.rename(columns={'tournament_score': 'metric_0005'}, inplace=True)

aggregated_df_all['update_time'] = pd.Timestamp.now()

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
aggregated_df_all.to_gbq(destination_table=f'{dataset_id}.{table_id}', project_id=project_id, if_exists='replace')

print("Data uploaded to BigQuery successfully.")