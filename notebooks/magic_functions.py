import pandas as pd
import numpy as np
from numpy import random

def update_1_step(Sent, Reward, N, arms):

    B = random.beta(Reward + 1, (Sent-Reward)+1, size = (N,arms))

    unique, counts = np.unique(np.argmax(B, axis = 1), return_counts=True)
    P_sus = counts/B.shape[0]
    
    proba = [P_sus[np.where(unique==i)][0] if i in unique.tolist() else 0 for i in range(arms)]

    return proba

def real_time(df, outdegree_df, N, arms, user_info_2):
    dataset = pd.DataFrame({'trials':range(1,df.shape[0]+1), 
              '1': 0,
              '2': 0,
              '3': 0,
              '4': 0,
              '5': 0,
              '6': 0,
              '7': 0,
              '8': 0,
              '9': 0,
              '10': 0})
        
    experiment = {'1':{'Sent':0,'Reward':0}, 
             '2':{'Sent':0,'Reward':0},
             '3':{'Sent':0,'Reward':0},
             '4':{'Sent':0,'Reward':0},
             '5':{'Sent':0,'Reward':0}, 
             '6':{'Sent':0,'Reward':0},
             '7':{'Sent':0,'Reward':0},
             '8':{'Sent':0,'Reward':0},
             '9':{'Sent':0,'Reward':0},
             '10':{'Sent':0,'Reward':0}}

    date_l = min(df.date_sent)
    old_outdegree = outdegree_df.iloc[:
                  outdegree_df.index.values.searchsorted(np.datetime64(date_l))].groupby('sender_id', as_index = False).size()
    
    old_outdegree = user_info_2.merge(old_outdegree, left_on = 'user_id', right_on = 'sender_id', how= 'left')
    old_outdegree.loc[old_outdegree['size'].isnull(), 'size'] = 0 
    old_outdegree = old_outdegree[['user_id', 'size']].set_index('user_id')
    
    for i in range(df.shape[0]):
        date_h = df.iloc[i,:]['date_sent']
        
        new_outdegree = outdegree_df.iloc[outdegree_df.index.values.searchsorted(np.datetime64(date_l)):
                  outdegree_df.index.values.searchsorted(np.datetime64(date_h))].groupby('sender_id', as_index = False).size()
        
        old_outdegree = old_outdegree.add(new_outdegree.set_index('sender_id'), fill_value=0)
        old_outdegree['decile'] = pd.qcut(old_outdegree['size'], 10, labels=False, duplicates='drop') + 1
        old_outdegree['decile'] = old_outdegree[['decile']]    
        
        experiment[str(int(old_outdegree.iloc[i]['decile']))]['Sent'] += 1
        experiment[str(int(old_outdegree.iloc[i]['decile']))]['Reward'] += df.iloc[i, -1]
        Sent = np.array([a[1]['Sent'] for a in experiment.items()])
        Reward = np.array([a[1]['Reward'] for a in experiment.items()])

        dataset.loc[i, ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']] = np.transpose(update_1_step(Sent, Reward, N, arms)) 
        date_h = date_l
        print('.', end='')
        
    return dataset


def mab_user_parallel(df, outdegree_df, user_id, N, arms, user_info_2):
    print(user_id)
    data = pd.DataFrame()
    res = real_time(df[df.user_id == user_id], outdegree_df, N, arms, user_info_2)
    res['user_id'] = user_id
    data = pd.concat([data, res])
    print('{} finished'.format(user_id))
    return data
