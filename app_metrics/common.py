# ● country - last country we see the player in
# ● avg_price_10 - avg. of last (maximum) 10 deposits prices
# ● last_weighted_daily_matches_count_10_played_days - metric is a weighted
# average of the number of matches a player played on their last 10 active days. The
# weighting is assigned based on recency: the most recent day gets the highest
# weight of 10, and the oldest of these days gets the lowest weight of 1. If there are
# fewer than 10 active days available, the weights are adjusted to range from 1 to
# the number of days the player was active, ensuring that recent activity is given
# greater emphasis.
# ● active_days_since_last_purchase - amount of active days (active day = day in
# which we see some data from the player, which means he logged in) since last
# purchase to current moment. If a player purchased today - it is 0.
# ● score_perc_50_last_5_days - the median score the player reached in matches in
# the last 5 calendar days. If he has no matches in the last 5 days - return null
METRICS = {
    "country":1,
    "avg_price_10":2,
    "active_days_since_last_purchase":3,
    "active_days_since_last_purchase":4,
    "score_perc_50_last_5_days":5
}
