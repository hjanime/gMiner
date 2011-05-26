# Project name #
gm_project_name = 'gMiner'
gm_project_long_name = 'gFeatMiner'
gm_project_version = '1.3.1'
gm_doc_url = 'http://bbcf.epfl.ch/gMiner'

# Current path #
gm_path = ''

# Convert formats or not #
gm_convert_dict = {
    'bed': 'sql',
    'gff': 'sql',
    'wig': 'sql',
}

# File types to extensions #
gm_known_extensions = {
    'SQLite 3.x database':                       'sql',
    'SQLite database (Version 3)':               'sql',
    'Hierarchical Data Format (version 5) data': 'hdf5',
}

# Default track fields #
gm_qualitative_fields  = ['start', 'end', 'name', 'score', 'strand']
gm_quantitative_fields = ['start', 'end', 'score']

# Field types #
gm_field_types = {
    'start':        'integer',
    'end':          'integer',
    'score':        'real',
    'strand':       'integer',
    'name':         'text',
    'thick_start':  'integer',
    'thick_end':    'integer',
    'item_rgb':     'text',
    'block_count':  'integer',
    'block_sizes':  'text',
    'block_starts': 'text',
}

# Chromosome names #
gm_chromosome_name_dictionary = {
    'MT':       'Q',
    'chrMito':  'Q',
    'chrM':     'Q',
    '2-micron': 'R',
    '2micron':  'R',
}

# Terminal colors #
gm_terminal_colors = {
    'end':    '\033[0m',    # Text Reset
    'blink':  '\033[5m',    # Blink
    'txtblk': '\033[0;30m', # Black - Regular
    'txtred': '\033[0;31m', # Red
    'txtgrn': '\033[0;32m', # Green
    'txtylw': '\033[0;33m', # Yellow
    'txtblu': '\033[0;34m', # Blue
    'txtpur': '\033[0;35m', # Purple
    'txtcyn': '\033[0;36m', # Cyan
    'txtwht': '\033[0;37m', # White
    'bldblk': '\033[1;30m', # Black - Bold
    'bldred': '\033[1;31m', # Red
    'bldgrn': '\033[1;32m', # Green
    'bldylw': '\033[1;33m', # Yellow
    'bldblu': '\033[1;34m', # Blue
    'bldpur': '\033[1;35m', # Purple
    'bldcyn': '\033[1;36m', # Cyan
    'bldwht': '\033[1;37m', # White
    'unkblk': '\033[4;30m', # Black - Underline
    'undred': '\033[4;31m', # Red
    'undgrn': '\033[4;32m', # Green
    'undylw': '\033[4;33m', # Yellow
    'undblu': '\033[4;34m', # Blue
    'undpur': '\033[4;35m', # Purple
    'undcyn': '\033[4;36m', # Cyan
    'undwht': '\033[4;37m', # White
    'bnkblk': '\033[5;30m', # Black - Blinking
    'bnkred': '\033[5;31m', # Red
    'bnkgrn': '\033[5;32m', # Green
    'bnkylw': '\033[5;33m', # Yellow
    'bnkblu': '\033[5;34m', # Blue
    'bnkpur': '\033[5;35m', # Purple
    'bnkcyn': '\033[5;36m', # Cyan
    'bnkwht': '\033[5;37m', # White
    'bakblk': '\033[40m',   # Black - Background
    'bakred': '\033[41m',   # Red
    'bakgrn': '\033[42m',   # Green
    'bakylw': '\033[43m',   # Yellow
    'bakblu': '\033[44m',   # Blue
    'bakpur': '\033[45m',   # Purple
    'bakcyn': '\033[46m',   # Cyan
    'bakwht': '\033[47m',   # White
}

# Debuging #
def trace(): __import__('IPython').Debugger.Pdb(color_scheme='Linux').set_trace()
def pudb():  __import__('pudb').set_trace()

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
