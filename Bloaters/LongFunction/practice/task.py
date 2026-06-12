# example input data, hardcoded for demo purpose
from dataclasses import dataclass
from typing import List, Dict

example_plays = {
    "hamlet": {"name": "Hamlet", "type": "tragedy"},
    "as-like": {"name": "As You Like It", "type": "comedy"},
    "othello": {"name": "Othello", "type": "tragedy"},
}

example_invoices = [
    {
        "customer": "BigCo",
        "performances": [
            {"playID": "hamlet", "audience": 55},
            {"playID": "as-like", "audience": 35},
            {"playID": "othello", "audience": 40},
        ],
    }
]

@dataclass(frozen=True)
class StatementData:
    @dataclass(frozen=True)
    class Performance:
        play_name: str
        amount: int
        audience: int
    customer: str
    performances: List[Performance]
    total_amount: int
    volume_credits: int


def compute_statement_data(invoice, plays) -> StatementData:
    def play_for(invoice, plays):
        return plays[invoice["playID"]]

    def amount_for(perf, play):
        if play["type"] == "tragedy":
            this_amount = 40000
            if perf["audience"] > 30:
                this_amount += 1000 * (perf["audience"] - 30)
        elif play["type"] == "comedy":
            this_amount = 30000
            if perf["audience"] > 20:
                this_amount += 10000 + 500 * (perf["audience"] - 20)
            this_amount += 300 * perf["audience"]
        else:
            raise ValueError(f"unknown type: {play['type']}")
        return this_amount

    def volume_credits_for(perf, play):
        credits = max(perf["audience"] - 30, 0)
        if "comedy" == play["type"]:
            credits += perf["audience"] // 5
        return credits

    def total_amount(data):
        return sum(p.amount for p in data)
    performances = []
    volume_credits = 0
    for perf in invoice["performances"]:
        play = play_for(perf, plays)
        amount = amount_for(perf, play)
        vc = volume_credits_for(perf, play)
        volume_credits += vc
        performances.append(StatementData.Performance(amount=amount, audience=perf["audience"], play_name=play["name"]))
    return StatementData(
        customer=invoice["customer"],
        performances=performances,
        total_amount=total_amount(performances),
        volume_credits=volume_credits,
    )

def render_plain_text(statement_data: StatementData) -> str:
    result = f"Statement for {statement_data.customer}\n"
    for perf in statement_data.performances:
        result += f"  {perf.play_name}: ${perf.amount / 100:.2f} ({perf.audience} seats)\n"
    result += f"Amount owed is ${statement_data.total_amount / 100:.2f}\n"
    result += f"You earned {statement_data.volume_credits} credits\n"
    return result


def statement(invoice, plays):
    return render_plain_text(compute_statement_data(invoice, plays))

if __name__ == "__main__":
    print(statement(example_invoices[0], example_plays))
