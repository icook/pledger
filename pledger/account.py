class Account(object):
    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

class NamedAccount(Account):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "'%s'" % self.name

    def add_prefix(self, prefix):
        name = ":".join(prefix + [self.name])
        return NamedAccount(name)
