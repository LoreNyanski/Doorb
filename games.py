# literally just blackjack

# literally just rollies - make it weighted

import pandas as pd

# -----------------------------------------------------------------------------------------
#                                   Wokeness quiz
# -----------------------------------------------------------------------------------------

# fetch the new db from https://wokedetector.cirnoslab.me/full-list
def updatedb():
    pass

# appid - name - banner - woke - description
def getwoke():
    df = pd.read_csv('.\csv\wokedata.csv')
    item = df[df['woke'] != 1].sample(n=1)
    return item

getwoke()