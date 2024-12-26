import pandas as pd
import csv
import datetime

from collections import defaultdict


default_values_userdata = {'money':0,'last_daily':datetime.datetime.min,'bet_user_id':0,'bet_amount':0}

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

    # making sure theres no KeyValueError
    def user_pre(self, user):
        if not user in self.userdata.index:
            self.userdata.loc[user] = default_values_userdata

    # Wrappers
    def op_data(func):
        def ret(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.save_data()
        return ret
    
    def op_userdata(func):
        def ret(self, user_id, *args, **kwargs):
            self.user_pre(user_id)
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

    # Change money of user
    def add_money(self, user_id, amount):
        self.userdata.loc[user_id, 'money'] += amount

    # Add new instance of dumbassery 
    @op_data
    def new_dumbass(self, user_id, time):
        self.data[user_id].append(time)
        return

    # save datas
    def save_data(self):
        with open('.\\csv\\data.csv', mode='w', newline='') as file:  
            writer = csv.writer(file)
            for user_id in self.data:
                writer.writerow([user_id] + self.data[user_id])

    def save_userdata(self):
        self.userdata.to_csv('.\\csv\\userdata.csv')
    

    @op_userdata
    def daily(self, user_id, amount):
        self.add_money(user_id, amount)
        self.userdata.loc[user_id, 'last_daily'] = datetime.datetime.now()

    @op_userdata
    def bet(self, user_id, bet_user_id, bet_amount):
        self.userdata.loc[user_id, 'bet_user_id'] = bet_user_id
        self.userdata.loc[user_id, 'bet_amount'] = bet_amount

    @op_userdata
    def clearbets(self):
        self.userdata['bet_user_id'] = 0
        self.userdata['bet_amount'] = 0

    def stats():
        pass

if __name__ == "__main__":
    dm = Door_manager()
    print(dm.data)
    dm.save_data()