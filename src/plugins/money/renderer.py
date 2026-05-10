from datetime import datetime

from .money_schema import time_until_midnight, Account

def render_rollies(roll):
    response = f'''
    ```
                    Min: 
                    1
    {roll}
                    Max: 
                    1000

    ####################
    ##### Generate #####
    ####################
    ```
    '''
    return response

def render_balance(account: Account, now: datetime):
    response = []
    if account.can_claim_daily():
        response.append("Daily available :D")
    else:
        delta_time = time_until_midnight(now)
        response.append(f"Daily available in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s)")
    response.append(f"You're balance: {account.balance}")

def render_charity():
    ...