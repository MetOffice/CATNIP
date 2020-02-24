"""
written by gredmond, some bits taken from hadts.
"""

import re
from six import string_types

def umstash_2_pystash(stash):
    """
    Function to take um style stash codes e.g. 24, 05216
    and convert them into 'python' stash codes e.g.m01s00i024, m01s05i216
   
    args
    ----
    stash: a tuple, list or string of stash codes
    
    Returns
    -------
    stash_list: a list of python stash codes


    Some basic examples:
    
    >>> sc = '24'
    >>> umstash_2_pystash(sc)
    ['m01s00i024']
    >>> sc = '24','16222','3236'
    >>> umstash_2_pystash(sc)
    ['m01s00i024', 'm01s16i222', 'm01s03i236']
    >>> sc = ['1','15201']
    >>> umstash_2_pystash(sc)
    ['m01s00i001', 'm01s15i201']

    Now test that it fails when appropriate:
    
    >>> sc = '-24'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: stash item -24 contains non-numerical characters. Numbers only
    >>> sc = '1234567'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    IndexError: stash item is 1234567. Stash items must be no longer than 5 characters
    >>> sc = 'aaa'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: stash item aaa contains non-numerical characters. Numbers only
    >>> sc = '24a'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: stash item 24a contains non-numerical characters. Numbers only
    >>> sc = 24, 25
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: 24 must be a string
    """

    stash_list = []
    # if stash is only one variable, it will be considered a string
    # and split, this statement checks for that case and puts
    # stash into a tuple to prevent splitting.
    if isinstance(stash, string_types):
        stash = tuple([stash])
    for scode in stash:
        if not isinstance(scode, string_types):
            raise TypeError('{} must be a string'.format(scode))
        if len(scode) > 5:
            raise IndexError("stash item is {}. Stash items must be no longer than 5 characters".format(scode))
        if not scode.isdigit():
            raise AttributeError('stash item {} contains non-numerical characters. Numbers only'.format(scode))

        # to split 3223 in to sec=3 and item=223
        sec, item = re.match('(\d{2})(\d{3})', scode.zfill(5)).groups()
        # to create a string m01s02i223   (if sec=03, and item=223)
        stash_list.append('m01s{}i{}'.format(sec, item))

    return stash_list

if __name__ == "__main__":
    import doctest
    doctest.testmod()
