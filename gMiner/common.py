"""
Common stuff used in several places.
"""

###############################################################################
def split_thousands(s, tSep='\'', dSep='.'):
    """
    Splits a number on thousands.

    >>> split_thousands(1000012)
    "1'000'012"
    """
    if s is None: return 0
    if not isinstance(s, str): s = str(s)
    cnt=0
    numChars=dSep+'0123456789'
    ls=len(s)
    while cnt < ls and s[cnt] not in numChars: cnt += 1
    lhs = s[0:cnt]
    s = s[cnt:]
    if dSep == '':
        cnt = -1
    else:
        cnt = s.rfind( dSep )
    if cnt > 0:
        rhs = dSep + s[ cnt+1: ]
        s = s[ :cnt ]
    else:
        rhs = ''
    splt=''
    while s != '':
        splt= s[ -3: ] + tSep + splt
        s = s[ :-3 ]
    return lhs + splt[ :-1 ] + rhs

###############################################################################
def wrap_string(s, width):
    """
    Wrap a string to the specified width.

    >>> wrap_string('aaabbb', 3)
    'aaa\\nbbb'
    """
    import textwrap
    wrapper = textwrap.TextWrapper()
    wrapper.width = width
    return '\n'.join(wrapper.wrap(s))

###############################################################################
def andify_strings(list_of_strings):
    """
    Given a list of strings will join them with commas
    and a final "and" word.

    >>> andify_strings(['Apples', 'Oranges', 'Mangos'])
    'Apples, Oranges and Mangos'
    """
    result = ', '.join(list_of_strings)
    comma_index = result.rfind(',')
    if comma_index > -1: result = result[:comma_index] + ' and' + result[comma_index+1:]
    return result

###############################################################################
def natural_sort(item):
    """
    Sort strings that contain numbers correctly.

    ::

        >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
        >>> l.sort(key=natural_sort)
        >>> l.__repr__()
        "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    """
    if item is None: return 0
    import re
    def try_int(s):
        try: return int(s)
        except ValueError: return s
    return map(try_int, re.findall(r'(\d+|\D+)', item))

###############################################################################
def sort_table(table, cols):
    """
    Sorts a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0

    >>> sort_table([['B','D'],['A','C'],['B','C'],['A','D']], (1,0))
    [['A', 'C'], ['B', 'C'], ['A', 'D'], ['B', 'D']]
    """
    import operator
    for col in reversed(cols):
        table = sorted(table, key=operator.itemgetter(col))
    return table

###############################################################################
def sentinelize(iterable, sentinel):
    """
    Add an item to the end of an iterable

    >>> list(sentinelize(range(4), 99))
    [0, 1, 2, 3, 99]
    """
    for item in iterable: yield item
    yield sentinel

###############################################################################
def import_module(name, path):
    """
    Import a module that is not in sys.path
    given it's relative path
    """
    import imp
    file, pathname, description = imp.find_module(name, [path])
    try:
        return imp.load_module(name, file, pathname, description)
    finally:
        if file: file.close()

###############################################################################
class collapse(object):
    """
    Collapse lists in specific ways

    >>> collapse.by_adding([1,5,2])
    8
    >>> collapse.by_adding([3])
    3
    >>> collapse.by_appending([[1,5],[5,3],[2,1]])
    [1, 5, 5, 3, 2, 1]
    >>> collapse.by_appending([[1,2,3]])
    [1, 2, 3]
    >>> collapse.by_union([[1,5],[5,3],[2,1]])
    [1, 2, 3, 5]
    >>> collapse.by_intersection([[1,5,4],[5,3,3],[2,6,5]])
    [5]
    """

    @staticmethod
    def by_adding(l):
        return sum(l)

    @staticmethod
    def by_appending(l):
        return [x for y in l for x in y]

    @staticmethod
    def by_union(l):
        return list(set(collapse.by_appending(l)))

    @staticmethod
    def by_intersection(l):
        return list(reduce(set.intersection, map(set,l)))

###############################################################################
def temporary_path(suffix=''):
    """
    Often, one needs a new random and temporary file path
    instead of the random and temporary file object provided
    by the 'tempfile' module.
    """
    import tempfile
    file = tempfile.NamedTemporaryFile(suffix=suffix)
    path = file.name
    file.close()
    return path

###############################################################################
def get_this_module_path():
    """ Will return the absolute path of the file containing
        this function"""
    # One way #
    import os
    from inspect import getfile, currentframe
    return os.path.abspath(getfile(currentframe()))
    # Another way #
    # return os.path.realpath(__file__)

###############################################################################
def make_latex_string(string):
    """
    >>> make_latex_string('lorem_ipsum dolor_sit')
    'lorem\\\_ipsum\\\ dolor\\\_sit'
    """

    import re
    string = re.sub('_', '\_', string)
    string = re.sub(' ', '\ ', string)
    return string

###############################################################################
class Color:
    """Shortcuts for the ANSI escape sequences to control
       formatting, color, etc. on text terminals. Use it like this::

            print Color.red + "Hello world" + Color.end
    """
    # Special #
    end = '\033[0m'
    # Regular #
    blk   = '\033[0;30m' # Black
    red   = '\033[0;31m' # Red
    grn   = '\033[0;32m' # Green
    ylw   = '\033[0;33m' # Yellow
    blu   = '\033[0;34m' # Blue
    pur   = '\033[0;35m' # Purple
    cyn   = '\033[0;36m' # Cyan
    wht   = '\033[0;37m' # White
    # Bold #
    bold  = '\033[1m'
    b_blk = '\033[1;30m' # Black
    b_red = '\033[1;31m' # Red
    b_grn = '\033[1;32m' # Green
    b_ylw = '\033[1;33m' # Yellow
    b_blu = '\033[1;34m' # Blue
    b_pur = '\033[1;35m' # Purple
    b_cyn = '\033[1;36m' # Cyan
    b_wht = '\033[1;37m' # White
    # Light #
    light = '\033[2m'
    l_blk = '\033[2;30m' # Black
    l_red = '\033[2;31m' # Red
    l_grn = '\033[2;32m' # Green
    l_ylw = '\033[2;33m' # Yellow
    l_blu = '\033[2;34m' # Blue
    l_pur = '\033[2;35m' # Purple
    l_cyn = '\033[2;36m' # Cyan
    l_wht = '\033[2;37m' # White
    # Italic #
    italic = '\033[1m'
    i_blk = '\033[3;30m' # Black
    i_red = '\033[3;31m' # Red
    i_grn = '\033[3;32m' # Green
    i_ylw = '\033[3;33m' # Yellow
    i_blu = '\033[3;34m' # Blue
    i_pur = '\033[3;35m' # Purple
    i_cyn = '\033[3;36m' # Cyan
    i_wht = '\033[3;37m' # White
    # Underline #
    underline = '\033[4m'
    u_blk = '\033[4;30m' # Black
    u_red = '\033[4;31m' # Red
    u_grn = '\033[4;32m' # Green
    u_ylw = '\033[4;33m' # Yellow
    u_blu = '\033[4;34m' # Blue
    u_pur = '\033[4;35m' # Purple
    u_cyn = '\033[4;36m' # Cyan
    u_wht = '\033[4;37m' # White
    # Glitter #
    flash = '\033[5m'
    g_blk = '\033[5;30m' # Black
    g_red = '\033[5;31m' # Red
    g_grn = '\033[5;32m' # Green
    g_ylw = '\033[5;33m' # Yellow
    g_blu = '\033[5;34m' # Blue
    g_pur = '\033[5;35m' # Purple
    g_cyn = '\033[5;36m' # Cyan
    g_wht = '\033[5;37m' # White
    # Fill #
    f_blk = '\033[40m'   # Black
    f_red = '\033[41m'   # Red
    f_grn = '\033[42m'   # Green
    f_ylw = '\033[43m'   # Yellow
    f_blu = '\033[44m'   # Blue
    f_pur = '\033[45m'   # Purple
    f_cyn = '\033[46m'   # Cyan
    f_wht = '\033[47m'   # White

