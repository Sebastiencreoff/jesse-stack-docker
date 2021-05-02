#! /usr/bin/env python
from jesse.enums import timeframes

def timeframes_to_minutes(timeframe:timeframes):
    
    for sep, multiply in [ ('m', 1),('h', 60), ('D', 60 *24), ('W', 60 * 24 *7)]:
        if sep in timeframe:
            count = int(timeframe.split(sep)[0])
            return count * multiply