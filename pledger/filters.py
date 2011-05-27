from pledger.entry import Entry

class FilterCollection(object):
    def __init__(self):
        self.filters = { }

    def add_filter(self, filter, level = 0):
        self.filters.setdefault(level, [])
        self.filters[level].append(filter)

    def apply(self, transaction, account, amount):
        entries = [Entry(account, amount)]

        levels = self.filters.keys()
        levels.sort()

        for level in levels:
            filters = self.filters[level]
            new_entries = []
            for filter in filters:
                for entry in entries:
                    new_entries += filter.apply(transaction, entry)
            entries = new_entries

        return entries

class Filter(object):
    pass

class Predicate(object):
    def __init__(self, predicate):
        self.predicate = predicate

    def __call__(self, *args):
        return self.predicate(*args)

    def __and__(self, other):
        @Predicate
        def result(*args):
            return self(*args) and other(*args)
        return result

    def __or__(self, other):
        @Predicate
        def result(*args):
            return self(*args) or other(*args)
        return result

class Generator(object):
    def __init__(self, generator):
        self.generator = generator

    def __call__(self, *args):
        return self.generator(*args)

    def __add__(self, other):
        @Generator
        def result(*args):
            return self(*args) + other(*args)
        return result
Generator.identity = Generator(lambda x: [x])
Generator.null = Generator(lambda x: [])

class RuleFilter(Filter):
    def __init__(self, predicate, generator, complement = Generator.identity):
        self.predicate = predicate
        self.generators = {
                True : generator,
                False : complement }

    def apply(self, transaction, entry):
        gen = self.generators[self.predicate(transaction, entry)]
        return gen(entry)

class AccountFilter(RuleFilter):
    def __init__(self, account):
        @Predicate
        def predicate(transaction, entry):
            return entry.account == account
        super(AccountFilter, self).__init__(predicate, Generator.identity, Generator.null)
