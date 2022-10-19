from src.utils import import_dta, import_tracks_dta, successful_creators_followers, calculate_avg_monthly_valence, stripplot
import datetime
import pandas as pd

path_dir = r"/Users/../Volumes/Raw/"

#outbound dfs:

df1 = import_dta(path_dir, "12sample_affiliations_sent.dta")
df1.columns = ['user_id', 'fan_id', 'date_sent']

#we will skip comments for now
import datetime
#affiliations :follows
#favoritings :likes

follows_sent = import_dta(path_dir, "12sample_affiliations_sent.dta")
comments_sent = import_dta(path_dir, "12sample_comments_made.dta")
shares_sent = import_dta(path_dir, "12sample_reposts_made.dta")
likes_sent = import_dta(path_dir, "12sample_favoritings_made.dta")

user_info = import_dta(path_dir, "12sample_user_infos.dta")
df13 = import_tracks_dta(path_dir, "12sample_tracks.dta")


########
follows_received = import_dta(path_dir, "12sample_aclffiliations_received.dta")
comments_received = import_dta(path_dir, "12sample_comments_received.dta")
shares_received = import_dta(path_dir, "12sample_reposts_received.dta")
likes_received = import_dta(path_dir, "12sample_favoritings_received.dta")

#dfplays = import_dta(path_dir, "12sample_plays_received.dta"


#Analysis
#create database with successful creators

#retain only top and bottom 10%
top10_bottom10_inf = successful_creators_followers(follows_received, 12, 0.1, 0.9)
valence_1_act = calculate_avg_monthly_valence(1, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info, only_active = True)
valence_3_act = calculate_avg_monthly_valence(3, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info, only_active = True)
valence_6_act = calculate_avg_monthly_valence(6, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info, only_active = True)
valence_9_act = calculate_avg_monthly_valence(9, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info, only_active = True)
valence_12_act = calculate_avg_monthly_valence(12, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info, only_active = True)

valence_1 = calculate_avg_monthly_valence(1, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info)
valence_3 = calculate_avg_monthly_valence(3, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info)
valence_6 = calculate_avg_monthly_valence(6, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info)
valence_9 = calculate_avg_monthly_valence(9, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info)
valence_12 = calculate_avg_monthly_valence(12, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, user_info)

df1 = top10_bottom10_inf.merge(valence_1, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df3 = top10_bottom10_inf.merge(valence_3, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df6 = top10_bottom10_inf.merge(valence_6, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df9 = top10_bottom10_inf.merge(valence_9, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df12 = top10_bottom10_inf.merge(valence_12, how = "inner", left_on = ['user_id'], right_on = ['user_id'])

df1_act = top10_bottom10_inf.merge(valence_1_act, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df3_act = top10_bottom10_inf.merge(valence_3_act, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df6_act = top10_bottom10_inf.merge(valence_6_act, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df9_act = top10_bottom10_inf.merge(valence_9_act, how = "inner", left_on = ['user_id'], right_on = ['user_id'])
df12_act = top10_bottom10_inf.merge(valence_12_act, how = "inner", left_on = ['user_id'], right_on = ['user_id'])

stripplot(df1, '1month')
stripplot(df3, '3month')
stripplot(df6, '6month')
stripplot(df9, '9month')
stripplot(df12, '12month')

stripplot(df1_act, 'Active_1month')
stripplot(df3_act, 'Active_3month')
stripplot(df6_act, 'Active_6month')
stripplot(df9_act, 'Active_9month')
stripplot(df12_act, 'Active_12month')
