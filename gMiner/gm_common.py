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
class gmCollapse(object):
    '''
    Collapse lists in specific ways

    >>> gmCollapse.by_adding([1,5,2])
    8
    >>> gmCollapse.by_adding([3])
    3
    >>> gmCollapse.by_appending([[1,5],[5,3],[2,1]])
    [1, 5, 5, 3, 2, 1]
    >>> gmCollapse.by_appending([[1,2,3]])
    [1, 2, 3]
    >>> gmCollapse.by_union([[1,5],[5,3],[2,1]])
    [1, 2, 3, 5]
    >>> gmCollapse.by_intersection([[1,5,4],[5,3,3],[2,6,5]])
    [5]
    '''

    @classmethod
    def by_adding(cls, l):
        return sum(l)

    @classmethod
    def by_appending(cls, l):
        return [x for y in l for x in y]     

    @classmethod
    def by_union(cls, l):
        return list(set(cls.by_appending(l)))

    @classmethod
    def by_intersection(cls, l):
        return list(reduce(set.intersection, map(set,l)))


###############################################################################   
def integer_to_roman(input):
    '''
    Convert an integer to roman numerals.

    >>> integer_to_roman(1999)
    'MCMXCIX'
    '''

    if type(input) != type(1):
       raise TypeError, "expected integer, got %s" % type(input)
    if not 0 < input < 4000:
       raise ValueError, "Argument must be between 1 and 3999"   
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = ""
    for i in range(len(ints)):
       count = int(input / ints[i])
       result += nums[i] * count
       input -= ints[i] * count
    return result

def roman_to_integer(input):
    '''
    Convert a roman numeral to an integer.

    >>> integers = range(1, 4000)
    >>> romans = [integer_to_roman(i) for i in integers]
    >>> back_to_integers = [roman_to_integer(r) for r in romans]
    >>> print integers == back_to_integers
    True
    '''

    if type(input) != type(""):
        raise TypeError, "expected string, got %s" % type(input)
    input = input.upper()
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    ints = [1000, 500, 100, 50,  10,  5,   1]
    places = []
    for c in input:
        if not c in nums:
            raise ValueError, "input is not a valid roman numeral: %s" % input
    for i in range(len(input)):
        c = input[i]
        value = ints[nums.index(c)]
        try:
            nextvalue = ints[nums.index(input[i +1])]
            if nextvalue > value:
                value *= -1
        except IndexError:
            pass
        places.append(value)
    sum = 0
    for n in places: sum += n
    if integer_to_roman(sum) == input:
        return sum
    else:
        raise ValueError, 'input is not a valid roman numeral: %s' % input


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
