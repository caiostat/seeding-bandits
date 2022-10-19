from src.utils import import_dta, import_tracks_dta, successful_creators_followers,\
gen_active_relations, get_fan_interactions_per_week, calculate_avg_monthly_valence,\
gen_active_relations_prob, get_fan_interactions_per_week_prob, stripplot_prob,\
reaction_probability, follower_list, filter_quantile, sample_creators_music,\
gen_outbound_creators, aggregate_received_interactions

import datetime
import numpy as np

def imp_reaction_probability(month, follows_sent, shares_sent, likes_sent, comments_sent, tracks,
                         follows_received, shares_received, likes_received, comments_received,
                         messages_received,
                         fanbase_analysis = False, per_week = False, non_fans_only = False,
                         messages_sent = None):

    df_action = gen_active_relations_prob(month, follows_sent, shares_sent, likes_sent,
                                          comments_sent, tracks , valence = False, messages_sent = messages_sent)
    df_action.drop(columns = ['interaction_week', 'interaction_year'], inplace = True)

    df_reaction = get_fan_interactions_per_week_prob(month, follows_received,
                                                     shares_received, likes_received, comments_received,
                                                     messages_received,tracks,
                                                     fanbase_analysis = fanbase_analysis, valence = False)
    df_reaction.reset_index(inplace = True)
    df_reaction['index'] = df_reaction['index'].astype(int)

    df_action = df_action.merge(df_reaction[['user_id', 'fan_id', 'date_sent', 'index']],
                                left_on = ['user_id','fan_id'], right_on = ['user_id','fan_id'],
                                suffixes = ['_action', '_reaction'], how = 'left')

    mask = ((df_action.date_sent_action < df_action.date_sent_reaction) &
            (df_action.date_sent_action > (df_action.date_sent_reaction - datetime.timedelta(weeks=1)))) |\
            df_action.date_sent_reaction.isnull()

    df_action["reaction_obtained"] = 0
    df_action.loc[mask,"reaction_obtained"] = 1

    df_action.loc[~mask,"date_sent_reaction"] = np.datetime64('NaT')

    df_action['reaction_interval'] =  df_action.date_sent_reaction - df_action.date_sent_action
    df_action.sort_values("reaction_interval", axis=0, ascending=True, inplace=True, na_position='last')
    df_action['duplicated_order'] = df_action.groupby("index").cumcount()

    mask = df_action.duplicated_order != 0
    df_action.loc[mask,"reaction_obtained"] = 0
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
        mask = (df_grouped.date_sent_action > df_grouped.follower_since) | (df_grouped.follower_since.isnull())
        df_grouped = df_grouped[mask]

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

def volume_analysis(follows_sent, follows_received, shares_sent, shares_received, likes_sent, likes_received,
                    comments_sent, comments_received,
                    tracks, fanbase_analysis = False,
                    non_fans_only = False,
                    messages_sent = None,
                    messages_received = None):

    sent_actions = gen_outbound_creators(follows_sent, shares_sent, likes_sent, comments_sent, tracks,
                                     messages_sent = messages_sent)
    received_reactions = aggregate_received_interactions(follows_received, shares_received,
                                                                   likes_received, comments_received,
                                                                   tracks,
                                                                   fanbase_analysis = fanbase_analysis,
                                                                   messages_received = messages_received)
    if fanbase_analysis:
        print('Obtaining fanbase...')
        followers = follower_list(follows_received)
        received_reactions = received_reactions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (received_reactions.date_sent > received_reactions.follower_since)
        received_reactions = received_reactions[mask]
        sent_actions = sent_actions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (sent_actions.date_sent > sent_actions.follower_since)
        sent_actions = sent_actions[mask]

    if non_fans_only:
        print('Dropping fanbase...')
        followers = follower_list(follows_received)
        received_reactions = received_reactions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (received_reactions.date_sent < received_reactions.follower_since) | (received_reactions.follower_since.isnull())
        received_reactions = received_reactions[mask]
        sent_actions = sent_actions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (sent_actions.date_sent < sent_actions.follower_since) | (sent_actions.follower_since.isnull())
        sent_actions = sent_actions[mask]

    actions_per_dyad_per_week = sent_actions.groupby(['user_id', 'fan_id', 'week_yr'], as_index = False).size()
    actions_per_dyad_per_week.columns = ['user_id', 'fan_id', 'week_yr', 'actions']

    reactions_per_dyad_per_week = received_reactions.groupby(['user_id', 'fan_id', 'week_yr'], as_index = False).size()
    reactions_per_dyad_per_week.columns = ['user_id', 'fan_id', 'week_yr', 'reactions']


    data_for_volume = actions_per_dyad_per_week.merge(reactions_per_dyad_per_week,
                                                 left_on = ['user_id', 'fan_id', 'week_yr'],
                                                 right_on=['user_id', 'fan_id', 'week_yr'],
                                                 how = 'outer')

    data_for_volume = data_for_volume.fillna(0)
    data_for_volume['volume'] = data_for_volume['reactions'] + data_for_volume['actions']

    data_for_volume = data_for_volume.groupby(['user_id', 'week_yr'], as_index = False).agg(avg_volume = ('volume', 'mean'))

    return data_for_volume


def valence_analysis(follows_sent, follows_received, shares_sent, shares_received, likes_sent, likes_received,
                    comments_sent, comments_received,
                    tracks, fanbase_analysis = False,
                    non_fans_only = False,
                    messages_sent = None,
                    messages_received = None):

    sent_actions = gen_outbound_creators(follows_sent, shares_sent, likes_sent, comments_sent, tracks,
                                     messages_sent = messages_sent)
    received_reactions = aggregate_received_interactions(follows_received, shares_received,
                                                                   likes_received, comments_received,
                                                                   tracks,
                                                                   fanbase_analysis = fanbase_analysis,
                                                                   messages_received = messages_received)
    if fanbase_analysis:
        print('Obtaining fanbase...')
        followers = follower_list(follows_received)
        received_reactions = received_reactions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (received_reactions.date_sent > received_reactions.follower_since)
        received_reactions = received_reactions[mask]
        sent_actions = sent_actions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (sent_actions.date_sent > sent_actions.follower_since)
        sent_actions = sent_actions[mask]

    if non_fans_only:
        print('Dropping fanbase...')
        followers = follower_list(follows_received)
        received_reactions = received_reactions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (received_reactions.date_sent < received_reactions.follower_since) | (received_reactions.follower_since.isnull())
        received_reactions = received_reactions[mask]
        sent_actions = sent_actions.merge(followers, right_on = ['user_id', 'fan_id'],
                                      left_on = ['user_id', 'fan_id'], how = 'left')
        mask = (sent_actions.date_sent < sent_actions.follower_since) | (sent_actions.follower_since.isnull())
        sent_actions = sent_actions[mask]


    actions_per_dyad_per_week = sent_actions.groupby(['user_id', 'fan_id', 'week_yr'], as_index = False).size()
    actions_per_dyad_per_week.columns = ['user_id', 'fan_id', 'week_yr', 'actions']

    reactions_per_dyad_per_week = received_reactions.groupby(['user_id', 'fan_id', 'week_yr'], as_index = False).size()
    reactions_per_dyad_per_week.columns = ['user_id', 'fan_id', 'week_yr', 'reactions']


    data_for_valence = actions_per_dyad_per_week.merge(reactions_per_dyad_per_week,
                                                 left_on = ['user_id', 'fan_id', 'week_yr'],
                                                 right_on=['user_id', 'fan_id', 'week_yr'],
                                                 how = 'outer')

    data_for_valence = data_for_valence.fillna(0)
    data_for_valence['valence'] = data_for_valence['reactions'] - data_for_valence['actions']

    data_for_valence = data_for_valence.groupby(['user_id', 'week_yr'], as_index = False).agg(avg_valence = ('valence', 'mean'))

    return data_for_valence
