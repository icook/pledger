from pledger.transaction import Transaction
from pledger.ledger_processor import LedgerProcessor
import util

class Ledger(object):
    def __init__(self, transactions):
        self.transactions = transactions

    def all_matching(self, predicate):
        return itertools.ifilter(predicate, self.entries)

    def add(self, transaction):
        self.transactions.append(transaction)

    def process(self):
        processor = LedgerProcessor(self)
        processor.run()
        return processor

    @property
    def entries(self):
        return itertools.chain(*self.transactions)

    @classmethod
    def parse(self, str):
        f = lambda line: line == ""
        lines = str.split("\n")
        transactions = [Transaction.parse(group) for group in util.itersplit(f, lines)]
        return Ledger(transactions)
