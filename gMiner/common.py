"""
=====================
Module: gMiner.common
=====================

Common stuff used in several places.
"""

###############################################################################
def split_thousands(s, tSep='\'', dSep='.'):
    '''
    Splits a number on thousands.

    >>> split_thousands(1000012)
    "1'000'012"
    '''

    if s == None: return 0
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
    '''
    Wrap a string to the specified width.

    >>> wrap_string('aaabbb', 3)
    'aaa\\nbbb'
    '''

    import textwrap
    wrapper = textwrap.TextWrapper()
    wrapper.width = width
    return '\n'.join(wrapper.wrap(s))

###############################################################################
def andify_strings(list_of_strings):
    '''
    Given a list of strings will join them with commas
    and a final "and" word.

    >>> andify_strings(['Apples', 'Oranges', 'Mangos'])
    'Apples, Oranges and Mangos'
    '''

    result = ', '.join(list_of_strings)
    comma_index = result.rfind(',')
    if comma_index > -1: result = result[:comma_index] + ' and' + result[comma_index+1:]
    return result

###############################################################################
def natural_sort(item):
    '''
    Will sort strings that contain numbers correctly

    >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
    >>> l.sort(key=natural_sort)
    >>> l.__repr__()
    "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    '''
    import re
    def try_int(s):
        try: return int(s)
        except: return s
    return map(try_int, re.findall(r'(\d+|\D+)', item))


###############################################################################
def sort_table(table, cols):
    '''
    Sorts a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0

    >>> sort_table([['B','D'],['A','C'],['B','C'],['A','D']], (1,0))
    [['A', 'C'], ['B', 'C'], ['A', 'D'], ['B', 'D']]
    '''
    import operator
    for col in reversed(cols):
        table = sorted(table, key=operator.itemgetter(col))
    return table

###############################################################################
def sentinelize(iterable, sentinel):
    '''
    Add an item to the end of an iterable

    >>> list(sentinelize(range(4), 99))
    [0, 1, 2, 3, 99]
    '''
    for item in iterable: yield item
    yield sentinel

###############################################################################
def import_module(name, path):
    '''
    Import a module that is not in sys.path
    given it's relative path
    '''
    import imp
    file, pathname, description = imp.find_module(name, [path])
    try:
        return imp.load_module(name, file, pathname, description)
    finally:
        if file: file.close()

###############################################################################
class collapse(object):
    '''
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
    '''

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
def named_temporary_path(suffix=''):
    ''' Often, one needs a new random and temporary file path
        instead of the random and temporary file object provided
        by the tempfile module'''
    import tempfile
    file = tempfile.NamedTemporaryFile(suffix=suffix)
    path = file.name
    file.close()
    return path

###############################################################################
class memoized_method(object):
    '''Decorator that caches a function's return value the first time
    it is called. If called later, the cached value is returned, and
    not re-evaluated

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.

    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:
    class Obj(object):
        @memoized_method
        def add_to(self, arg):
            return self + arg
    Obj.add_to(1)    # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached
    '''
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, objtype=None):
        from functools import partial
        if obj is None:
            return self.func
        return partial(self, obj)
    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res


###############################################################################
def get_this_module_path():
    ''' Will return the absolute path of the file containing
        this function'''
    import os
    from inspect import getfile, currentframe
    return os.path.abspath(getfile(currentframe()))
    return os.path.realpath(__file__)

###############################################################################
def make_latex_string(string):
    '''
    >>> make_latex_string('lorem_ipsum dolor_sit')
    'lorem\\\_ipsum\\\ dolor\\\_sit'
    '''

    import re
    string = re.sub('_', '\_', string)
    string = re.sub(' ', '\ ', string)
    return string

###############################################################################
def number_to_color(num=0):
    '''
    Takes a number, returns a color

    >>> number_to_color(7)
    'pink'
    '''

    num = int(num) % 8
    return {
        0: 'blue',
        1: 'green',
        2: 'red',
        3: 'cyan',
        4: 'magenta',
        5: 'orange',
        6: 'black',
        7: 'pink'
    }[num]


def number_to_color_light(num=0):
    num = int(num) % 8
    return {
        0: '#87CEFA', #'lightblue',
        1: '#90EE90', #'lightgreen',
        2: '#FFB6C1', #'lightpink',
        3: '#48D1CC', #'mediumturquoise',
        4: '#EE82EE', #'violet',
        5: '#FFD700', #'gold',
        6: '#C0C0C0', #'silver',
        7: '#FFFAF0', #'floralwhite'
    }[num]
