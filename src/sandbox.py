from utils import import_dta, import_tracks_dta, gen_outbound_creators#, filter_outbound
path_dir = r"/Users/../Volumes/Raw/"
import datetime
#affiliations :follows
#favoritings :likes

follows_sent = import_dta(path_dir, "12sample_affiliations_sent.dta")
comments_sent = import_dta(path_dir, "12sample_comments_made.dta")
shares_sent = import_dta(path_dir, "12sample_reposts_made.dta")
likes_sent = import_dta(path_dir, "12sample_favoritings_made.dta")

user_info = import_dta(path_dir, "12sample_user_infos.dta")
df13 = import_tracks_dta(path_dir, "12sample_tracks.dta")

dfa = gen_outbound_creators(df1,df7,df10, df12)
filtered_df = filter_outbound(dfa, datetime.datetime(2013,4,1,0,0,0))

########
follows_received = import_dta(path_dir, "12sample_affiliations_received.dta")
comments_received = import_dta(path_dir, "12sample_comments_received.dta")
shares_received = import_dta(path_dir, "12sample_reposts_received.dta")
likes_received = import_dta(path_dir, "12sample_favoritings_received.dta")

#dfplays = import_dta(path_dir, "12sample_plays_received.dta")

top10_bottom10_inf = successful_creators_followers(follows_received, 12, 0.1, 0.9)
df1 = reaction_probability(1)

df1 = top10_bottom10_inf.merge(df1, how = "inner", left_on = ['user_id'], right_on = ['user_id'])

stripplot_prob(df1, '1month')
