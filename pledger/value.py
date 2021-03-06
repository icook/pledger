# Copyright (C) 2011 by Paolo Capriotti <p.capriotti@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from decimal import Decimal, InvalidOperation, ROUND_DOWN
import re

class Value(object):
    def __init__(self, values, precision=2):
        self.values = values
        self.precision = precision

    def currencies(self):
        return (currency for currency,amount in self.values.iteritems() if amount != 0)

    def components(self, currencies = None):
        if currencies is None:
            currencies = sorted(self.currencies())
        if len(currencies):
            result = []
            for currency in currencies:
                amount = self.values.get(currency, 0)
                if amount:
                    result.append(Value({currency: amount}))
                else:
                    result.append(ZERO)
            return result
        else:
            return [ZERO]

    def null(self):
        for currency, amount in self.values.iteritems():
            if amount != 0: return False
        return True

    def negative(self):
        for currency, amount in self.values.iteritems():
            if amount > 0: return False
        return not self.null()

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return (self - other).null()

    def __add__(self, other):
        result = dict(self.values)
        for currency in other.values:
            amount = other.values[currency]
            if currency in result:
                result[currency] += amount
            else:
                result[currency] = amount
        return Value(result, max(self.precision, other.precision))

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        result = { }
        for currency in self.values:
            result[currency] = -self.values[currency]
        return Value(result, self.precision)

    def __mul__(self, num):
        result = { }
        for currency in self.values:
            unit = Decimal(10) ** -self.precision
            result[currency] = (self.values[currency] * num).quantize(unit)
        return Value(result, self.precision)

    def __lt__(self, other):
        return (self - other).negative()

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return (other - self).negative()

    def __ge__(self, other):
        return self == other or self > other

    def format_value(self, curr, value):
        places = self.precision
        q = Decimal(10) ** -places      # 2 places --> '0.01'
        sign, digits, exp = value.quantize(q).as_tuple()
        result = []
        digits = map(str, digits)
        build, next = result.append, digits.pop
        build(" " + curr)
        for i in range(places):
            build(next() if digits else '0')
        build('.')
        if not digits:
            build('0')
        i = 0
        while digits:
            build(next())
            i += 1
        if sign: build('-')
        return ''.join(reversed(result))

    def __str__(self):
        if self.null():
            return "0"
        else:
            return ", ".join([self.format_value(curr, value) for
                              curr, value in self.values.iteritems()])

    def __repr__(self):
        return "<%s>" % " ".join([self.format_value("?", value) for
                                 curr, value in self.values.iteritems()])

    def __hash__(self):
        return hash(tuple(sorted(self.values.items())))

    @classmethod
    def parse(cls, str, precision=None):
        elements = re.split(r"\s+", str)
        if len(elements) == 2:
            try:
                amount = Decimal(elements[0])
                if precision is None:
                    p = elements[0].find('.')
                    if p == -1:
                        precision = 2
                    else:
                        precision = len(elements[0 ]) - p - 1
                currency = elements[1]
                return Value({ currency: amount }, precision=precision)
            except InvalidOperation:
                return None

ZERO = Value({}, 0)
