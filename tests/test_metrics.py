import os

import pandas as pd

from notebooks.pandas_file_to_big_query import calculate_metrics


def test_metrics():
    folder_path = 'tests_resources/raw_data/'
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.parquet')]

    df = pd.concat([pd.read_parquet(f) for f in all_files])
    # df = df[df['player_id'] == '6671adc2dd588a8bda035feb']
    df = df[df['player_id'] == '6671adc2dd588a8bda0367bb']

    aggregated_df = calculate_metrics(df)
    # {'player_id': {0: '6671adc2dd588a8bda0367bb'},
    #  'country': {0: 'NL'},
    #  'avg_price_10': {0: 89.0},
    #  'last_weighted_daily_matches_count_10_played_days':{0: 46.388888888888886},
    #  'active_days_since_last_purchase': {0: 167},
    #  'score_perc_50_last_5_days': {0: -1.0}}
    employees = aggregated_df.to_dict()

    assert employees['country'][0] == 'NL'
    assert employees['avg_price_10'][0] == 89.0

    assert employees['last_weighted_daily_matches_count_10_played_days'][0] == 46.388888888888886
    assert employees['active_days_since_last_purchase'][0] == 167
    assert employees['score_perc_50_last_5_days'][0] == -1.0


test_metrics()
