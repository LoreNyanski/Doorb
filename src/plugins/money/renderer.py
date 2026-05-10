from datetime import datetime

from .money_schema import time_until_midnight, Account, Transaction

def render_rollies(roll):
    response = f'''```
                Min: 
                1
{roll}
                Max: 
                1000

####################
##### Generate #####
####################```
    '''
    return response

def render_balance(account: Account, now: datetime):
    response = []
    if account.can_claim_daily(now):
        response.append("Daily available :D")
    else:
        delta_time = time_until_midnight(now)
        response.append(f"Daily available in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s)")
    response.append(f"You're balance: {account.balance}")
    return "\n".join(response)

def render_charity(sender: Account):
    return f'Money transfered\n(New balance: {sender.balance})'