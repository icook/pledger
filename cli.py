from argparse import ArgumentParser
from pledger.report import reports
from pledger.filter import Filter
from pledger.parser import Parser
from pledger.sorting import MapSorting
from pledger.rule import RuleCollection
from pledger.template import default_template
import re, os, sys

parser = Parser()
filter = Filter.null
rules = RuleCollection()
sorting = MapSorting(lambda x: x.transaction.date)
template = default_template

def run_cli():
    global filter

    argparser = ArgumentParser()
    argparser.add_argument("report", action="store")
    argparser.add_argument("--filename", action="store", nargs=1)
    argparser.add_argument("patterns", metavar="PATTERN", type=str,
                           nargs="*")

    args = argparser.parse_args()

    report_factory = reports.get(args.report)
    if report_factory is None:
        raise Exception("no such report " + args.report)
    filters = [Filter.matches(re.compile(pattern)) for pattern in args.patterns]
    if filters:
        filter &= reduce(Filter.__or__, filters)

    filename = os.environ.get("PLEDGER")
    if filename is None:
        filename = args.filename[0]

    if filename is None:
        sys.stderr.write("No ledger specified\n")
        sys.exit(1)

    ledger = parser.parse_ledger(open(filename).read())
    report = report_factory(ledger, rules, filter, sorting)
    print template(report)
