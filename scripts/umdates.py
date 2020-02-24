'''
Various utility functions below for dealing with PRECIS and UM date stamps.
'''
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from six import string_types
from datetime import datetime, timedelta
# when all scitools versions with netcdftime are retired we can remove this
# try - except
try:
    from netcdftime import datetime as cdatetime
except ImportError:
    from cftime import datetime as cdatetime

def convertFromUMStamp(datestamp, fmt):
    ''' Convert UM date stamp to normal python date.
    DOES NOT SUPPORT 3 monthly seasons e.g. JJA as described in the manual
    http://www.metoffice.gov.uk/binaries/content/assets/mohippo/pdf/4/m/tech_man_v2.pdf#page=119

    args
    ----
    datestamp: UM datestamp
    fmt: either 'YYMMM' or 'YYMDH'

    returns
    -------
    dt: datetime object of the input datestamp

    >>> print (convertFromUMStamp('k5bu0', 'YYMDH'))
    2005-11-30 00:00:00

    '''
    # Check input
    if (len(datestamp) != 5) or (fmt not in ('YYMMM', 'YYMDH')):
        raise ValueError('Problem with input arguments {} {}'.format(datestamp,
                                                                     fmt))

    # First calculate decades since 1800
    d = precisD2(datestamp[0])
    # calculate year
    yr = 1800 + (d * 10) + int(datestamp[1])

    # calculate month and if necessary day and hour
    if fmt == 'YYMMM':
        mon = datetime.strptime(datestamp[2:5], '%b').month
        dt = datetime(year=yr, month=mon, day=1)
    else:
        # This is a YYMDH so need to convert day and hour as well
        mon = precisD2(datestamp[2])
        d = precisD2(datestamp[3])
        hr = precisD2(datestamp[4])
        dt = datetime(year=yr, month=mon, day=d, hour=hr)

    return dt

def convertToUMStamp(dt, fmt):
    '''
    Convert python datetime object or netcdf datetime object
    into UM date stamp.
    http://www.metoffice.gov.uk/binaries/content/assets/mohippo/pdf/4/m/tech_man_v2.pdf#page=119

    args
    ----
    dt: Python datetime object to convert
    fmt: either 'YYMMM' or 'YYMDH'. Will not convert seasonal (e.g. JJA)


    returns
    -------
    UMstr: string with UMdatestamp

    >>> dt = datetime(1981, 11, 2)
    >>> print (dt, convertToUMStamp(dt, 'YYMMM'))
    1981-11-02 00:00:00 i1nov
    >>> print (dt, convertToUMStamp(dt, 'YYMDH'))
    1981-11-02 00:00:00 i1b20
    >>> dt = cdatetime(1981, 2, 30)
    >>> print (dt, convertToUMStamp(dt, 'YYMMM'))
    1981-02-30 00:00:00 i1feb
    >>> print (dt, convertToUMStamp(dt, 'YYMDH'))
    1981-02-30 00:00:00 i12u0
    '''

    if not isinstance(dt, datetime)  and not isinstance(dt, cdatetime):
        raise ValueError('Datetime format incorrect: {}'.format(type(dt)))

    if fmt not in ('YYMMM', 'YYMDH'):
        raise ValueError('Problem with format type {}'.format(fmt))

    # First convert years
    YY = precisYY(dt.year)

    if fmt == 'YYMMM':
        # just need to format the month as 3 character string
        mon = dt.strftime('%b').lower()
        UMstr = '{}{}'.format(YY, mon)
    else:
        mon = precisD2(dt.month)
        d = precisD2(dt.day)
        hr = precisD2(dt.hour)
        UMstr = '{}{}{}{}'.format(YY, mon, d, hr)

    assert len(UMstr) == 5, 'UMstr {} wrong length\ndt = {}'.format(
                                UMstr, dt.strftime('%Y%m%d'))
    return UMstr

def precisYY(y):
    '''
    Convert year (int) into 2 character UM year

    args
    ----
    y: int


    returns
    -------
    YY: string 2 letter UM year character


    >>> print (precisYY(1973))
    h3

    '''

    # use // operator to round down (integer division)
    decades = y // 10
    onedigityrs = y - (decades * 10)
    decades = precisD2(decades - 180)
    YY = '{}{}'.format(decades, onedigityrs)
    return YY

def precisD2(c):
    ''' Convert characters according to PRECIS table D2
    http://www.metoffice.gov.uk/binaries/content/assets/mohippo/pdf/4/m/tech_man_v2.pdf#page=119

    args
    ----
    c: character or number to convert
    Supply a character to convert from left to right in the table
    Supply an int to convert from right to left in the table

    >>> print (precisD2('1'))
    1
    >>> print (precisD2('c'))
    12
    >>> print (precisD2('s'))
    28

    Also does the reverse conversions:
    >>> print (precisD2(1))
    1
    >>> print (precisD2(12))
    c
    >>> print (precisD2(28))
    s

    returns
    -------
    conv: converted value: int if input is string, string if input is int

    '''
    if isinstance(c, string_types):
        # Throw error if non alpha numeric string supplied
        if not c.isalnum():
            raise ValueError('Out of bounds argument {}'.format(c))
        # Converting left to right
        try:
            # Try converting from integer
            conv = int(c)
        except ValueError:
            # It's a character, so use ord() function to convert
            # to correct number
            conv = ord(c) - 87
    else:
        # Throw error if too large or too small number supplied
        if c < 0 or c > 35:
            raise ValueError('Out of bounds argument {}'.format(c))
        # Converting right to left
        if c <= 9:
            # Just convert to string
            conv = str(c)
        else:
            # Calculate correct letter to convert to using chr()
            conv = chr(c + 87)

    return conv

def UMFileList(runid, startd, endd, freq):
    ''' Give a (thoretical) list of UM date format files between 2 dates.
    Assuming no missing dates.

    args
    ----
    runid: model runid
    startd: start date(date)
    endd: end date(date)
    freq:
    Specifies frequency of data according to PRECIS technical manual
    table D1
    http://www.metoffice.gov.uk/binaries/content/assets/mohippo/pdf/4/m/tech_man_v2.pdf#page=118
    Currently only supports:
    pa: Timeseries of daily data spanning 1 month (beginning 0z on the 1st day)
    pj: Timeseries of hourly data spanning 1 day (0z - 24z)
    pm: Monthly average data for 1 month
    Not currently supported: ps, px, p1, p2, p3, p4, mY

    returns
    -------
    filelist: list of strings giving the filenames

    >>> runid = 'akwss'
    >>> startd = datetime(1980, 9, 1)
    >>> endd = datetime(1980, 9, 3)
    >>> freq = 'pa'
    >>> print (UMFileList(runid, startd, endd, freq)) # doctest: +NORMALIZE_WHITESPACE
    ['akwssa.pai0910.pp', 'akwssa.pai0920.pp', 'akwssa.pai0930.pp']

    >>> startd = datetime(1980, 9, 1)
    >>> endd = datetime(1980, 12, 31)
    >>> freq = 'pm'
    >>> print (UMFileList(runid, startd, endd, freq)) # doctest: +NORMALIZE_WHITESPACE
    ['akwssa.pmi0sep.pp', 'akwssa.pmi0oct.pp',
     'akwssa.pmi0nov.pp', 'akwssa.pmi0dec.pp']

    '''

     # list to store the output
    filelist = []

    dt = startd
    while dt <= endd:
        # Monthly frequency
        if freq == 'pm':
            fname = '{}a.pm{}.pp'.format(runid,
                                         convertToUMStamp(dt, 'YYMMM'))
            # Add a month to the date
            if dt.month == 12:
                dt = dt.replace(year = dt.year + 1, month = 1)
            else:
                dt = dt.replace(month = dt.month + 1)

        # Daily frequency
        elif freq == 'pa':
            # build file name string
            fname = '{}a.pa{}.pp'.format(runid,
                                         convertToUMStamp(dt, 'YYMDH'))
            # add a day to the date
            dt = dt + timedelta(days=1)

        # Hourly frequency
        elif freq == 'pj':
            # build file name string
            fname = '{}a.pj{}.pp'.format(runid,
                                         convertToUMStamp(dt, 'YYMDH'))
            # add a day to the date
            dt = dt + timedelta(days=1)

        # Not recognized frequency
        else:
            raise ValueError('Unsupported freq {} supplied.'.format(freq))

        # Add to list
        filelist.append(fname)

    return filelist

if __name__ == '__main__':
    import doctest
    doctest.testmod()
