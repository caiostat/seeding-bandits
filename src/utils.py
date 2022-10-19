import os
import pandas as pd
import numpy as np
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from functools import reduce



def import_dta(path_dir, path_or_buffer):
    """Imports and parsers dta data, string timestamp is converted to datatime.datetime format"""
    data = pd.read_stata(os.sep.join([path_dir, path_or_buffer]))
    data["created_at"] = pd.to_datetime(data["created_at"])
    print("%" * 10, path_or_buffer, "%" * 10)
    print(data.shape)
    return data


def import_tracks_dta(path_dir, path_or_buffer):
    """Imports and parsers dta data"""
    data = pd.read_stata(os.sep.join([path_dir, path_or_buffer]))
    data["created_date"] = pd.to_datetime(data["created_date"])
    print("%" * 10, path_or_buffer, "%" * 10)
    print(data.shape)
    return data


def gen_outbound_creators(follows_sent, shares_sent, likes_sent, comments_sent, tracks, messages_sent = None, filter_creators = True):
    follows_sent['outbound_activity'] = 'follow'
    follows_sent.columns = ['user_id', 'fan_id', 'date_sent', 'outbound_activity']

    if 'song_id' in shares_sent.columns:
        shares_sent.drop(columns=["song_id"])
    shares_sent = shares_sent[['reposter_id', "owner_id", 'created_at']]
    shares_sent['outbound_activity'] = 'share'
    shares_sent.columns = ['user_id', 'fan_id', 'date_sent', 'outbound_activity']

    if 'track_id' in likes_sent.columns:
        likes_sent.drop(columns=["track_id"], inplace=True)
    likes_sent['outbound_activity'] = 'like'
    likes_sent.columns = ['user_id', 'fan_id', 'date_sent', 'outbound_activity']

    if 'track_id' in comments_sent.columns:
        comments_sent.drop(columns=["track_id"], inplace=True)
    comments_sent['outbound_activity'] = 'comment'
    comments_sent.columns = ['user_id', 'fan_id', 'date_sent', 'outbound_activity']

    if messages_sent is not None:
        messages_sent["outbound_activity"] = 'message'
        messages_sent.columns = ['user_id', 'fan_id', 'date_sent', 'outbound_activity']
        df = pd.concat([follows_sent, shares_sent, likes_sent, comments_sent, messages_sent])
    else:
        df = pd.concat([follows_sent, shares_sent, likes_sent, comments_sent])

    if filter_creators:
        df = df[df['user_id'].isin(tracks.user_id.unique())]

    df['interaction_week'] = df.date_sent.apply(lambda x: x.week)
    df['interaction_year'] = df.date_sent.apply(lambda x: x.year)
    df['week_yr'] = df.date_sent.dt.strftime('%Y-w%U')
    df = df.loc[df['user_id'] != df['fan_id'],:]
    #pd.to_datetime(df['interaction_year'].astype(str) + ' ' + df['interaction_week'].astype(str) + ' 1',
    #format='%Y %U %w')

    return df


def gen_active_relations(month, follows_sent, shares_sent, likes_sent, comments_sent, tracks,valence = False):
    df = gen_outbound_creators(follows_sent, shares_sent, likes_sent, comments_sent,  tracks,
                                     messages_sent = messages_sent)
    # df.columns = ['fan_id', 'user_id', 'date_sent', 'type', 'created_at'] #check later
    # df with the outbound activities by creators
    delta_M = datetime.timedelta(days=month * 30)
    date = dt.datetime(2013, 3, 1, 0, 0, 0) + delta_M
    print('Active date:{}'.format(date))
    delta = dt.timedelta(days=30)
    mask = (df['date_sent'] > (date)) & (df['date_sent'] < (date + delta))
    df = df[mask]
    if valence:
        df = df.groupby(['user_id', 'fan_id'], as_index=False).size()
    df = df.loc[df.fan_id != df.user_id, :]
    return df

def gen_active_relations_prob(month, follows_sent, shares_sent, likes_sent, comments_sent, tracks, valence = False, messages_sent = None):
    df = gen_outbound_creators(follows_sent, shares_sent, likes_sent, comments_sent, tracks,
                                     messages_sent = None)
    # df.columns = ['fan_id', 'user_id', 'date_sent', 'type', 'created_at'] #check later
    # df with the outbound activities by creators
    if month == 999:
        delta_M = datetime.timedelta(days=month * 0)
        delta = datetime.timedelta(days=10000)
    else:
        delta_M = datetime.timedelta(days=month * 30)
        delta = datetime.timedelta(days=30)
    date = datetime.datetime(2013, 3, 1, 0, 0, 0) + delta_M
    print('Active date:{}'.format(date))
    mask = (df['date_sent'] > (date)) & (df['date_sent'] < (date + delta))
    df = df[mask]
    if valence:
        df = df.groupby(['user_id', 'fan_id'], as_index=False).size()
    df = df.loc[df.fan_id != df.user_id, :]
    return df

def get_fan_interactions_per_week(month, follows_received, shares_received, likes_received, comments_received, tracks, fanbase_analysis = False, valence = False):
    # creates dataframe with the outbound activies by fans
    delta_M = datetime.timedelta(days=month * 30)
    delta = datetime.timedelta(weeks=4)
    date = datetime.datetime(2013, 3, 1, 0, 0, 0) + delta_M
    print('Interaction date:{}'.format(date))
    follows_received['inbound_activity'] = 'follow'
    follows_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'song_id' in shares_received:
        shares_received.drop(columns=["song_id"])
    shares_received = shares_received[['reposter_id', "owner_id", 'created_at']]
    shares_received['inbound_activity'] = 'share'
    shares_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'track_id' in likes_received:
        likes_received = likes_received.drop(columns=["track_id"])
    likes_received['inbound_activity'] = 'like'
    likes_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'track_id' in comments_received:
        comments_received = comments_received.drop(columns=["track_id"])
    comments_received['inbound_activity'] = 'comment'
    comments_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    mask1 = (follows_received['date_sent'] >= (date)) & (follows_received['date_sent'] <= (date + delta))
    mask2 = (shares_received['date_sent'] >= (date)) & (shares_received['date_sent'] <= (date + delta))
    mask3 = (likes_received['date_sent'] >= (date)) & (likes_received['date_sent'] <= (date + delta))
    mask4 = (comments_received['date_sent'] >= (date)) & (comments_received['date_sent'] <= (date + delta))

    if fanbase_analysis:
        df = pd.concat([shares_received[mask2], likes_received[mask3], comments_received[mask4]])
    else:
        df = pd.concat([follows_received[mask1], shares_received[mask2], likes_received[mask3], comments_received[mask4]])

    df['interaction_week'] = df.date_sent.apply(lambda x: x.week)
    df['interaction_year'] = df.date_sent.apply(lambda x: x.year)
    df['week_yr'] = pd.to_datetime(df['interaction_year'].astype(str) + ' ' + df['interaction_week'].astype(str) + ' 1',
                                format='%Y %U %w')
    df = df.loc[df.fan_id != df.user_id, :]

    if valence:
        df = df.groupby(["user_id", "fan_id", "week_yr"], as_index=False).size()
    #df.columns = ["user_id", "fan_id", "interaction_week", 'interactions', 'inbound_activity']
    df = df[df['user_id'].isin(tracks.user_id.unique())]

    return df

def get_fan_interactions_per_week_prob(month, follows_received,
                                       shares_received,
                                       likes_received,
                                       comments_received,
                                       messages_received,
                                       tracks,
                                       fanbase_analysis = False,
                                       valence = False):
    # creates dataframe with the outbound activies by fans
    if month == 999:
        delta_M = datetime.timedelta(days=month * 0)
        delta = datetime.timedelta(days=10000)
    else:
        delta_M = datetime.timedelta(days=month * 30)
        delta = datetime.timedelta(days=37)
    date = datetime.datetime(2013, 3, 1, 0, 0, 0) + delta_M
    print('Interaction date:{}'.format(date))
    follows_received['inbound_activity'] = 'follow'
    follows_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'song_id' in shares_received:
        shares_received.drop(columns=["song_id"])
    shares_received = shares_received[['reposter_id', "owner_id", 'created_at']]
    shares_received['inbound_activity'] = 'share'
    shares_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'track_id' in likes_received:
        likes_received = likes_received.drop(columns=["track_id"])
    likes_received['inbound_activity'] = 'like'
    likes_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'track_id' in comments_received:
        comments_received = comments_received.drop(columns=["track_id"])
    comments_received['inbound_activity'] = 'comment'
    comments_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    messages_received["outbound_activity"] = 'message'
    messages_received.columns = ['user_id', 'fan_id', 'date_sent', 'outbound_activity']

    if fanbase_analysis:
        df = pd.concat([shares_received, likes_received, comments_received, messages_received])
    else:
        df = pd.concat([follows_received, shares_received, likes_received, comments_received, messages_received])
    df['interaction_week'] = df.date_sent.apply(lambda x: x.week)
    df['interaction_year'] = df.date_sent.apply(lambda x: x.year)
    df['week_yr'] = pd.to_datetime(df['interaction_year'].astype(str) + ' ' + df['interaction_week'].astype(str) + ' 1',
                                format='%Y %U %w')
    df = df.loc[df.fan_id != df.user_id, :]

    if valence:
        df = df.groupby(["user_id", "fan_id", 'week_yr'], as_index=False).size()
    #df.columns = ["user_id", "fan_id", "interaction_week", 'interactions', 'inbound_activity']
    df = df[df['user_id'].isin(tracks.user_id.unique())]

    return df

def calculate_avg_monthly_valence(month, follows_sent, shares_sent, likes_sent, comments_sent, follows_received, shares_received, likes_received, comments_received, only_active = False):
    df_active = gen_active_relations(month, follows_sent, shares_sent, likes_sent, comments_sent, valence = True)
    df_active = df_active.drop(columns=['size'])
    df = get_fan_interactions_per_week(month, follows_received, shares_received, likes_received, comments_received)
    df = df.groupby(['user_id', 'fan_id'], as_index=False).size()
    df.columns = ['user_id', 'fan_id', 'valence']
    if only_active:
        df = df_active.merge(df, how="inner", left_on=['user_id', 'fan_id'], right_on = ['user_id', 'fan_id'])
    df = df.groupby(['user_id'], as_index=False).agg({'valence': 'mean'})

    return df


def successful_creators_music(df, month):
    delta_M = datetime.timedelta(days=month * 30)
    date = datetime.datetime(2013, 3, 1, 0, 0, 0) + delta_M
    delta = datetime.timedelta(weeks=4)
    mask = (df['created_at'] > date) & (df['created_at'] < date + delta)
    dfa = df[mask].groupby('owner_id', as_index=False).agg({"listener_id": ['count', pd.Series.nunique]})
    dfa.columns = ['_'.join(col).strip() for col in dfa.columns.values]
    return dfa


def successful_creators_filtered_music(df, perc1, perc2):
    low = np.quantile(df.listener_id_count, perc1)
    high = np.quantile(df.listener_id_count, perc2)

    mask = (df["listener_id_count"] <= low) | (df["listener_id_count"] >= high)
    df.loc[df["listener_id_count"] <= low, "high/low"] = "low"
    df.loc[df["listener_id_count"] >= high, "high/low"] = "high"
    df = df[mask]

    return df


#def successful_creators_followers(follows_received, month, always_same_batches = False, perc1 = None, perc2 = None):
#    delta_M = datetime.timedelta(days=month * 30)
#    date_fin = datetime.datetime(2013, 3, 1, 0, 0, 0) + delta_M
#    print(date_fin)

#    if 'inbound_activity' not in follows_received.columns:
#        follows_received.columns = ['fan_id', 'user_id', 'date_sent']

#    mask = (follows_received['date_sent'] < date_fin)

#    df = follows_received[mask].groupby('user_id', as_index=False).agg({'fan_id': pd.Series.nunique})
#    df.columns = ['user_id', 'followers']

#    if always_same_batches:
#        low = np.quantile(df.followers, perc1)
#        high = np.quantile(df.followers, perc2)

#        print("High influencer boundary: {}".format(high))
#        print("Low influencer boundary: {}".format(low))

#        mask = (df["followers"] <= low) | (df["followers"] >= high)
#        df.loc[df["followers"] <= low, "high_low"] = "low"
#        df.loc[df["followers"] >= high, "high_low"] = "high"
#        df = df[mask]

#    return df

def successful_creators_followers(follows_received, month, creators ,always_same_batches = False, perc1 = None, perc2 = None):
    delta_M = datetime.timedelta(days=month * 30)
    date_fin = datetime.datetime(2013, 3, 1, 0, 0, 0) + delta_M
    print(date_fin)

    if 'inbound_activity' not in follows_received.columns:
        follows_received.columns = ['fan_id', 'user_id', 'date_sent']

    mask = (follows_received['date_sent'] < date_fin)

    df = follows_received[mask].groupby('user_id', as_index=False).agg({'fan_id': pd.Series.nunique})
    df.columns = ['user_id', 'followers']

    creators = pd.DataFrame(creators.user_id.unique(), columns = ['user_id'])
    df = creators.merge(df, on = 'user_id', how = 'left')
    df.fillna(0, inplace = True)

    if always_same_batches:
        low = np.quantile(df.followers, perc1)
        high = np.quantile(df.followers, perc2)

        print("High influencer boundary: {}".format(high))
        print("Low influencer boundary: {}".format(low))

        mask = (df["followers"] <= low) | (df["followers"] >= high)
        df.loc[df["followers"] <= low, "high_low"] = "low"
        df.loc[df["followers"] >= high, "high_low"] = "high"
        df = df[mask]

    return df

def filter_quantile(df, perc1, perc2):
    low = np.quantile(df.followers, perc1)
    high = np.quantile(df.followers, perc2)

    print("High influencer boundary: {}".format(high))
    print("Low influencer boundary: {}".format(low))

    mask = (df["followers"] <= low) | (df["followers"] >= high)
    df.loc[df["followers"] <= low, "high_low"] = "low"
    df.loc[df["followers"] >= high, "high_low"] = "high"
    df = df[mask]

    return df


def stripplot(df, name):
    p = sns.stripplot(x = 'high_low', y = 'valence', data=df, jitter=0.1)
    p.set(xlabel = 'Creator level of success', ylabel = 'Mean relationship valence')
    sns.despine()
    plt.savefig('graphics/{}.png'.format(name))


def stripplot_prob(df, name):
    p = sns.stripplot(x = 'high_low', y = 'reaction_prob', data=df, jitter=0.1)
    p.set(xlabel = 'Creator level of success', ylabel = 'Mean reaction probability')
    sns.despine()
    plt.savefig('/Users/caiorego/Desktop/BDS/RA/Seeding-Bandits/graphics/probability/{}.png'.format(name))


def reaction_probability(month, follows_sent, shares_sent, likes_sent, comments_sent, tracks,
                         follows_received, shares_received, likes_received, comments_received,
                         fanbase_analysis = False, dyad_analysis = False, per_week = False,
                         non_fans_only = False):

    df_action = gen_active_relations_prob(month, follows_sent, shares_sent, likes_sent,
                                          comments_sent, tracks , valence = False)
    df_action.drop(columns = ['interaction_week', 'interaction_year'], inplace = True)

    df_reaction = get_fan_interactions_per_week_prob(month, follows_received,
                                                     shares_received, likes_received, comments_received, tracks,
                                                     fanbase_analysis = fanbase_analysis, valence = False)

    df_action = df_action.merge(df_reaction[['user_id', 'fan_id', 'date_sent']],
                                left_on = ['user_id','fan_id'], right_on = ['user_id','fan_id'],
                                suffixes = ['_action', '_reaction'], how = 'left')

    mask = ((df_action.date_sent_action < df_action.date_sent_reaction) &
            (df_action.date_sent_action > (df_action.date_sent_reaction - datetime.timedelta(weeks=1)))) |\
            df_action.date_sent_reaction.isnull()

    df_action = df_action[mask]
    #print('minimum action: {}'.format(min(df_action.date_sent_action)))
    #print('maximum action: {}'.format(max(df_action.date_sent_action)))

    #print('minimum reaction: {}'.format(min(df_action[df_action.date_sent_reaction.isnull()==False].date_sent_reaction)))
    #print('maximum reaction: {}'.format(max(df_action[df_action.date_sent_reaction.isnull()==False].date_sent_reaction)))

    df_grouped = df_action.groupby(['user_id', 'fan_id', 'date_sent_action', 'week_yr'], as_index = False)\
                .agg(interaction_responses =('date_sent_reaction', 'count'))
    df_grouped['reaction_obtained'] = (df_grouped.interaction_responses > 0).astype(int)

    if fanbase_analysis:
        print('Obtaining fanbase...')
        followers = follower_list(follows_received)
        df_grouped = df_grouped.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (df_grouped.date_sent_action > df_grouped.follower_since)
        df_grouped = df_grouped[mask]

    if non_fans_only:
        print('Dropping fanbase...')
        followers = follower_list(follows_received)
        df_grouped = df_grouped.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (df_grouped.date_sent_action < df_grouped.follower_since) or (df_grouped.follower_since.isnull())
        df_grouped = df_grouped[mask]

    if dyad_analysis:
        df_grouped = df_grouped.groupby(['user_id', 'fan_id']).agg('mean')

    if per_week:
        per_creator_prob = df_grouped.groupby(['user_id', 'fan_id', 'week_yr'], as_index = False)\
        .agg(avg_reaction_obtained = ('reaction_obtained', 'mean'))
        per_creator_prob = per_creator_prob.reset_index()
        print(per_creator_prob.columns)

        per_creator_prob.columns = (['index','user_id', 'fan_id', 'week_yr', 'reaction_prob'])
        per_creator_prob = df_grouped.groupby(['user_id', 'week_yr'], as_index = False)\
        .agg(avg_reaction_obtained = ('reaction_obtained', 'mean'))
        #per_creator_prob.columns = (['user_id', 'week_yr' 'reaction_prob'])

    else:
        per_creator_prob = df_grouped.groupby(['user_id']).agg(avg_reaction_obtained = ('reaction_obtained', 'mean'))
        per_creator_prob = per_creator_prob.reset_index()
        per_creator_prob.columns = (['user_id', 'reaction_prob'])

    return per_creator_prob

#def follower_list(month, follows_received):
#    delta_M = datetime.timedelta(days=month * 30)
#    date_fin = datetime.datetime(2013, 3, 1, 0, 0, 0) + delta_M

#    mask = (follows_received['date_sent'] <= (date_fin + delta))

#    followers = follows_received[mask].groupby(['user_id', 'fan_id']).size()
#    followers = followers.reset_index()
#    followers.drop(columns = [0], inplace = True)

#    return followers

def follower_list(follows_received):

    followers = follows_received[["fan_id", "user_id", "date_sent"]]
    followers.columns = ["fan_id", "user_id", "follower_since"]

    return followers

def sample_creators_music(df, days):
    date = datetime.datetime(2013, 3, 1, 0, 0, 0)
    delta = datetime.timedelta(days=days)
    mask = df.created_date <= (date + delta)
    df = df[mask]

    return df


def aggregate_received_interactions(follows_received, shares_received, likes_received, comments_received, tracks,
                                    fanbase_analysis = False,
                                    messages_received = None):
    follows_received['inbound_activity'] = 'follow'
    follows_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'song_id' in shares_received:
        shares_received.drop(columns=["song_id"])
    shares_received = shares_received[['reposter_id', "owner_id", 'created_at']]
    shares_received['inbound_activity'] = 'share'
    shares_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'track_id' in likes_received:
        likes_received = likes_received.drop(columns=["track_id"])
    likes_received['inbound_activity'] = 'like'
    likes_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if 'track_id' in comments_received:
        comments_received = comments_received.drop(columns=["track_id"])
    comments_received['inbound_activity'] = 'comment'
    comments_received.columns = ['fan_id', 'user_id', 'date_sent', 'inbound_activity']

    if (messages_received is not None) and (fanbase_analysis == False):
        messages_received["outbound_activity"] = 'message'
        messages_received.columns = ['user_id', 'fan_id', 'date_sent', 'outbound_activity']
        df = pd.concat([follows_received, shares_received, likes_received, comments_received, messages_received])
    elif fanbase_analysis and (messages_received is not None):
        df = pd.concat([shares_received, likes_received, comments_received, messages_received])
    elif fanbase_analysis:
        df = pd.concat([shares_received, likes_received, comments_received])
    else:
        df = pd.concat([follows_received, shares_received, likes_received, comments_received])

    df['interaction_week'] = df.date_sent.apply(lambda x: x.week)
    df['interaction_year'] = df.date_sent.apply(lambda x: x.year)
    df['week_yr'] = df.date_sent.dt.strftime('%Y-w%U')
    #pd.to_datetime(df['interaction_year'].astype(str) + ' ' + df['interaction_week'].astype(str) + ' 1',
                                #format='%Y %U %w')
    df = df.loc[df.fan_id != df.user_id, :]

    return df
