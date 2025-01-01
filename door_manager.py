import pandas as pd
import csv
import datetime
import bisect

from collections import defaultdict


default_values_userdata = {'money':500,'last_daily':pd.to_datetime(0),'bet_user_id':0,'bet_amount':0}
pd.options.mode.chained_assignment = None # I don't care pandas

class Door_manager:

    # Load data
    def __init__(self):
        self.data = defaultdict(list)
        with open('.\\csv\\data.csv') as file:
            for row in csv.reader(file):
                self.data[int(row[0])] = list(pd.to_datetime(row[1:]))

        self.userdata = pd.read_csv('.\\csv\\userdata.csv')
        self.userdata.set_index(['user_id'], inplace=True)
        self.userdata['last_daily'] = pd.to_datetime(self.userdata['last_daily'])

        self.bets = Bet(self.userdata[['bet_user_id', 'bet_amount']])
    
    # save datas
    def save_data(self):
        with open('.\\csv\\data.csv', mode='w', newline='') as file:  
            writer = csv.writer(file)
            for user_id in self.data:
                writer.writerow([user_id] + self.data[user_id])

    def save_userdata(self):
        self.userdata.to_csv('.\\csv\\userdata.csv')
    


    # making sure theres no KeyValueError
    def user_pre(self, user):
        if not user in self.userdata.index:
            self.userdata.loc[user] = default_values_userdata

    def no_bets(self):
        return self.bets.no_bets()

    # Wrappers
    def op_data(func):
        def ret(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.save_data()
        ret.original_function = func
        return ret
    def op_userdata(func):
        def ret(self, user_id=0, *args, **kwargs):
            if user_id != 0: self.user_pre(user_id)
            func(self, user_id, *args, **kwargs)
            self.save_userdata()
        return ret



    # Getters
    def get_money(self, user_id):
        self.user_pre(user_id)
        return self.userdata.loc[user_id, 'money']
    def get_bet(self, user_id):
        self.user_pre(user_id)
        return (self.userdata.loc[user_id, 'bet_user_id'], self.userdata.loc[user_id, 'bet_amount'])
    def get_last_daily(self, user_id):
        self.user_pre(user_id)
        return self.userdata.loc[user_id, 'last_daily']
    def get_delta_daily(self, user_id):
        return datetime.datetime.now() - self.get_last_daily(user_id)
    def get_last_incident(self, user_id):
        return self.data[user_id][-1]

    # Change money of user
    def add_money(self, user_id, amount):
        self.userdata.loc[user_id, 'money'] += amount



    # Add new instance of dumbassery 
    @op_data
    def new_dumbass(self, user_id, time):
        bisect.insort(self.data[user_id], time)
        return
    

    # Add money from daily
    @op_userdata
    def daily(self, user_id, amount):
        self.add_money(user_id, amount)
        self.userdata.loc[user_id, 'last_daily'] = datetime.datetime.now()

    # Register bet in userdata
    @op_userdata
    def place_bet(self, user_id, bet_user_id, bet_amount):
        self.add_money(user_id, self.userdata.loc[user_id, 'bet_amount'])
        self.userdata.loc[user_id, 'bet_user_id'] = bet_user_id
        self.userdata.loc[user_id, 'bet_amount'] = bet_amount
        self.add_money(user_id, -1*bet_amount)
        self.bets.add_bet(self.userdata.loc[user_id])

    # clear all bets in userdata
    @op_userdata
    def clearbets(self, user_id):
        self.userdata['bet_user_id'] = 0
        self.userdata['bet_amount'] = 0
        self.bets = Bet(self.userdata[['bet_user_id', 'bet_amount']])

    @op_data
    def cleardata(self, user_id=None):
        if user_id == None:
            self.data = defaultdict(list)
        else:
            self.data.pop(user_id)


    def stats(self, user_id, user_ids, stat):
        if stat == 'self':
            if len(self.data[user_id]) > 1:
                ehe = [len(self.data[user_id])]
                ehe = ehe + pd.Series(self.data[user_id], name='ehe').diff().aggregate(['mean', 'median', 'max', 'min']).to_list()
                ehe = ehe + [datetime.datetime.now(tz=datetime.timezone.utc) - self.get_last_incident(user_id)]
            else:
                ehe = 'Not enough data'
        else:
            # This way it takes the users from only ppl who already have data in csv, not the entire server
            # user_ids = self.data.keys()
            if stat == 'count':
                ehe = [(user, len(self.data[user])) for user in user_ids]
                ehe.sort(key= lambda x: x[1], reverse=True)
            elif stat == 'last':
                ehe = []
                for user in user_ids:
                    try:
                        ehe.append((user,datetime.datetime.now(tz=datetime.timezone.utc) - self.get_last_incident(user)))
                    except:
                        ehe.append((user,'Not enough data'))
                ehe.sort(key= lambda x: x[1] if not type(x[1]) == str else datetime.timedelta.min, reverse=True)
            else:
                ehe = [(user,pd.Series(self.data[user], name='ehe').diff().aggregate(stat)) if len(self.data[user]) > 1 
                       else (user,'Not enough data')
                       for user in user_ids]
                ehe.sort(key= lambda x: x[1] if not type(x[1]) == str else datetime.timedelta.max)
        return ehe

# --------------------------------------------------------------------------------------------
# 
# -------------------------------------------------------------------------------------------


# this doesn't seem very userful ngl since to initialize it you HAVE to give a dataframe with the 2 columns
# 'bet_user_id' and 'bet_amount' indexed by user id. So to say there woudln't really be any way to use this outside of
# Door manager, but it does help me with organising things so it stays
class Bet:

    def __init__(self, df):
        self.data = df[df['bet_user_id'] != 0] # ['bet_user_id', 'bet_amount', 'percent', 'payout'] indexed by userid of the person who put the bet
        self.table = None
        self.pool = None
        self.calcpool()
        self.calctable()
        self.calcpayouts()

    def calcpool(self):
        self.pool = self.data['bet_amount'].sum()
    def calctable(self):
        df = self.data[['bet_user_id', 'bet_amount']].groupby(['bet_user_id']).aggregate(['max', 'sum', 'count'])
        df.columns = ['max', 'amount', 'count']
        df.loc[:,'loser_wagers'] = self.pool - df['amount'].copy()
        df.loc[:,'percent'] = df['amount'].copy() / self.pool
        self.table = df.copy()
    def calcpayouts(self):
        self.data.loc[:,'percent'] = self.data['bet_amount'].copy() / self.table.loc[self.data['bet_user_id'].copy(), 'amount'].copy().values
        self.data['payouts'] = round(self.data['bet_amount'] + self.table.loc[self.data['bet_user_id'], 'loser_wagers'].values * self.data['percent']).astype(int)
        self.data.loc[:, 'payouts'] = self.data[['payouts', 'bet_amount']].apply(lambda row: max(row['payouts'], row['bet_amount']*1.25), axis=1)


    def add_bet(self, new_row):
        self.data.loc[new_row.name] = [new_row['bet_user_id'], new_row['bet_amount'], None, None]
        self.calcpool()
        self.calctable()
        self.calcpayouts()
    
    def get_payouts(self, correct_id):
        return self.data[self.data['bet_user_id']==correct_id]['payouts'].to_dict()

    def get_dumbass_candidates(self):
        table = pd.Series()
        return self.table.index.to_list()

    def no_bets(self):
        return self.data.empty

    def __str__(self):
        if self.no_bets(): return 'No bets yet'
        else:
            resp = self.table[['amount', 'percent']]
            resp['format'] = resp['percent'].apply(lambda x: f"{x * 100:.1f}%")
            resp['vis'] = resp['percent'].apply(lambda x: '█{message:{fill}<10}'.format(message = int(x*10)*'█', fill = '▒'))
            resp.drop(columns = 'percent', inplace=True)

            resp.columns = ['total bets', '%', '']
            resp.index.names = ['dumbass candidates']
            return f'''
```
{resp}
```
'''



if __name__ == "__main__":
    dm = Door_manager()
    print(dm.bets.data)
    print(dm.bets.table)
    # dm.clearbets()
    # print(dm.no_bets())
    print(dm.bets.get_payouts(3))
    # print(dm.bets)
    # print('{:10}'.format(6*'a'))
    # print(dm.stats(294910192154443779,[1,2,3,294910192154443779], 'min'))
    print(dm.bets)