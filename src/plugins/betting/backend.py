
import math as m
from dataclasses import dataclass
'''
TODO:
the pool betting system has a few issues:
- FIX SITUATION WHERE EVERYONE BETTING ON THE SAME PERSON GIVES NO REWARD
- FIX SITUATION WHERE IF YOU'RE THE ONLY BETTOR ON A SUBJECT YOU GET FULL POOL NO MATTER YOUR BET SIZE
(fixable through house liquidity injection)'''

class BetTable:

    def __init__(self):
        self.bets: list[Bet] = []

    def add_bet(self, bet :Bet) -> list[Bet]:
        self.bets.append(bet)

    def pool(self) -> int:
        return calc_pool([bet.amount for bet in self.bets])

    def subject_total(self, subject_id: int) -> int:
        return sum([bet.amount for bet in self.bets if bet.subject_id == subject_id])
    
    def subject_odds(self, subject_id: int) -> float:
        return calc_odds(self.pool(), self.subject_total(subject_id))
    
    def payouts(self, winner_id: int) -> list[tuple[Bet, int]]:
        odds = self.subject_odds(winner_id)
        return [(bet, bet.payout(odds)) for bet in self.bets if bet.subject_id == winner_id]
    
    def _aggregate_totals(self) -> dict[int, int]:
        totals = {}
        for bet in self.bets:
            totals[bet.subject_id] = totals.get(bet.subject_id, 0) + bet.amount
        return totals

    def summary(self) -> dict[int, dict]:
        totals = self._aggregate_totals()
        pool = sum(totals.values())

        return {
            subject: {
                "total": total,
                "odds": calc_odds(pool, total)
            }
            for subject, total in totals.items()
        }
    
@dataclass
class Bet:
    bettor_id: int
    subject_id: int
    amount: int

    def payout(self, odds: float) -> int:
        return calc_payout(self.amount, odds) 

def calc_pool(amounts: list[int]) -> int:
    return sum(amounts)

def calc_odds(pool: int, total_wager: int) -> float:
    return pool / total_wager

def calc_payout(amount: int, odds: float) -> int:
    return m.ceil(amount * odds)


### DEBUG SECTION ###
if __name__ == '__main__':
    table = BetTable()
    table.add_bet(Bet(0, 2, 500))
    table.add_bet(Bet(0, 3, 500))
    table.add_bet(Bet(1, 2, 300))
    table.add_bet(Bet(2, 3, 1))
    print(table.summary())
    print(table.payouts(3))