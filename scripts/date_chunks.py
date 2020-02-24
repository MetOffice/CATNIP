'''
CIID Tools: Create date chunks
Created by Hamish Steptoe (hamish.steptoe@metoffice.gov.uk)
Created on 11/12/18
'''
import datetime as dt
import itertools
import sys


def date_chunks(startdate, enddate, yearchunk, indatefmt='%Y/%m/%d', outdatefmt='%Y/%m/%d'):
    '''Make date chunks from min and max date range

    Make contiguous pairs of date intervals to aid chunking
    of MASS retrievals. Where the date interval is not a multiple
    of `yearchunk`, intervals of less than `yearchunk` may be returned.
    See ``Examples`` for useage.

    Arguments:
        startdate (string): Starting date (min date)
        enddate (string): Ending date (max date)
        yearchunk (int): Year chunks to split the date interval into
        indatefmt (string, optional): String format for input dates. Defaults to yyyy/mm/dd
        outdatefmt (string, optional): String format for ouput dates. Defaults to yyyy/mm/dd

    Returns:
          list: List of strings of date intervals

    Raises:
        ValueError: If `enddate` (ie. max date) is less than or equal to `startdate` (ie. min date)
        Excpetion: If `yearchunk` is not an integer
        Exception: If not using python 3

    Examples:
          >>> date_chunks('1851/1/1', '1899/12/31', 25)
          [('1851/01/01', '1875/12/26'), ('1875/12/26', '1899/12/31')]
          >>> date_chunks('1890/1/1', '1942/12/31', 25)
          [('1890/01/01', '1914/12/27'), ('1914/12/27', '1939/12/21'), ('1939/12/21', '1942/12/31')]

    Note:
        This function is only compatible with python 3.
        Author: Hamish Steptoe
    '''
    # Check python version
    if sys.version_info[0] < 3:
        raise Exception("Only compatible with Python 3")
    # Check yearchunk is integer
    if not isinstance(yearchunk, int):
        raise Exception("yearchunk must be an integer")
    # Convert strings to datetime objects
    mindate = dt.datetime.strptime(startdate, indatefmt)
    maxdate = dt.datetime.strptime(enddate, indatefmt)
    # Check dates
    if maxdate <= mindate:
        raise ValueError('Max date ({}) is <= min date ({})'.format(maxdate, mindate))
    # Find date steps
    dates = [mindate + dt.timedelta(days=x) for x in range(0, (maxdate - mindate).days, yearchunk * 365)]
    dates = [dt.datetime.strftime(d, outdatefmt) for d in dates]
    # Add final end date
    dates.append(dt.datetime.strftime(maxdate, outdatefmt))
    # Make contiguous date interval pairs
    a, b = itertools.tee(dates)
    next(b, None)
    return list(zip(a, b))
