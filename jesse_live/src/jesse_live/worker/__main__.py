#! /usr/bin/env python

import argparse

from jesse_live.worker.run import run

def main():
    parser = argparse.ArgumentParser("Live Runner")
    parser.add_argument(
        "-n", "--name", help="Strategy name", required=True)
    parser.add_argument(
        "-e", "--exchange", help="Exchange", required=True)
    parser.add_argument(
        "-s", "--symbol", help="Symbol", required=True)
    parser.add_argument(
        "-t", "--timeframe", help="TimeFrame", default='1m')
    parser.add_argument('--dev', dest='dev', action='store_true', default=False)

    args = parser.parse_args()
    run(args.name, args.exchange, args.symbol, args.timeframe, args.dev)


if __name__ == "__main__":
    main()