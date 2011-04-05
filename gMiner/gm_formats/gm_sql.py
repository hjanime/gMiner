# General Modules #
import sqlite3

# Modules #
from .. import gm_tracks    as gm_tra
from .. import gm_errors    as gm_err
from ..gm_constants import *

###########################################################################   
class gmFormat(gm_tra.gmTrack):
    '''
    Essential variables:
    - format: file extension code
    - type: quantitative or qualitative
    - all_chrs: a list of available chromosomes
    - chrmeta: information associated with chromosomes (length etc)
    - attributes: information associated with the track (source etc)
    '''

    def initialize(self):
        self.format = "sql"
        self.connection = sqlite3.connect(self.location)
        self.cursor = self.connection.cursor()
        try:
            # Get qual or quan #
            self.cursor.execute("select value from attributes where key='datatype'")
            self.type = self.cursor.fetchall()[0][0].encode('ascii')
            # List all tables #
            self.refresh_table_list()
            # List all chrs #
            self.cursor.execute("select name from chrNames")
            self.all_chrs  = [x[0].encode('ascii') for x in self.cursor.fetchall()]
            # Chr fields #
            self.get_chr_fields()
            # Chr metadata #
            self.get_chr_meta()    
            # General Attributes #
            self.get_meta_data()
        except sqlite3.OperationalError as err:
            raise gm_err.gmError("400", "The sql track " + self.name + " doesn't seem to have the correct format", err)

    def refresh_table_list(self):
        self.cursor.execute("select name from sqlite_master where type='table'")
        self.all_tables = [x[0].encode('ascii') for x in self.cursor.fetchall()]

    def get_meta_data(self):
        self.cursor.execute("select key, value from attributes")
        self.attributes = dict(self.cursor.fetchall())

    def get_chr_meta(self):
        self.cursor.execute("pragma table_info(chrNames)")
        chrkeys = [x[1] for x in self.cursor.fetchall()]
        self.cursor.execute("select * from chrNames")
        self.chrmeta = [dict([(k, e[i]) for i, k in enumerate(chrkeys)]) for e in self.cursor.fetchall()]

    def get_chr_fields(self):
        if self.all_chrs: self.fields = [x[1] for x in self.cursor.execute('pragma table_info("'+self.all_chrs[0]+'")').fetchall()]
    
    #-----------------------------------------------------------------------------#   
    @classmethod
    def make_new(cls, location, type, name):
        name = name #TODO
        connection = sqlite3.connect(location)
        cursor = connection.cursor()
        cursor.execute('create table chrNames (name text, length integer)') 
        cursor.execute('create table attributes (key text, value text)')
        if type == 'quantitative':
            cursor.execute('insert into attributes (key,value) values ("datatype","quantitative")') 
        if type == 'qualitative':
            cursor.execute('insert into attributes (key,value) values ("datatype","qualitative")') 
        connection.commit()
        cursor.close()
        connection.close()

    #-----------------------------------------------------------------------------#   
    def get_data_qual(self, selection, fields):
        def get_chr(chr):
            if chr not in self.all_tables: return []
            return self.cursor.execute("select " + ','.join(fields) + " from '" + chr +"'")
        def get_span(span):
            chr = span['chr']
            if chr not in self.all_tables: return []
            condition = "start < " + str(span['end']) + " and " + "end > " + str(span['start'])
            return self.cursor.execute("select " + ','.join(fields) + " from '" + chr + "' where " + condition)
        if selection['type'] == 'span':
            return get_span(selection['span'])
        if selection['type'] == 'chr':
            return get_chr(selection['chr'])

    def get_data_quan(self, selection, fields = ['start', 'end', 'score']):
        return self.get_data_qual(selection, fields)
    
    def get_stored(self, type, subtype, selection):
        return False #TODO

    def write_data_qual(self, chr, iterable, fields):
        if chr in [x[0] for x in self.cursor.execute("select name from sqlite_master where type='table'").fetchall()]:
            self.cursor.execute("drop table " + chr)
        columns = ','.join([field + ' ' + gm_field_types[field] for field in fields])
        self.cursor.execute('create table "' + chr + '" (' + columns + ')')
        self.cursor.executemany('insert into "' + chr + '" values (' + ','.join(['?' for x in range(len(fields))])+')', iterable)
        self.connection.commit()
        #for f in iterable:
        #    values = ','.join(map(lambda x: type(x)==str and "'" + str(x) + "'" or str(x), f)) 
        #    self.cursor.execute('insert into ' + chr + ' values (' + values + ')')

    def write_data_quan(self, chr, iterable, fields):
        if chr in [x[0] for x in self.cursor.execute("select name from sqlite_master where type='table'").fetchall()]:
            self.cursor.execute("drop table " + chr)
        self.cursor.execute('create table "' + chr + '"  (start integer, end integer, score real)')
        self.cursor.executemany('insert into "' + chr + '"  values (?,?,?)', iterable)
        self.connection.commit()

    def write_meta_data(self, data):
        for k in data.keys(): self.cursor.execute('insert into attributes (key,value) values (?,?)',(k,data[k]))

    def write_chr_meta(self, data):
        # data = [{u'length': 197195432, u'name': u'chr1'},
        #         {u'length': 129993255, u'name': u'chr10'},
        #         {u'length': 121843856, u'name': u'chr11'},
        #         {u'length': 121257530, u'name': u'chr12'}]
        for x in data: self.cursor.execute('insert into chrNames (' + ','.join(x.keys()) + ') values (' + ','.join(['?' for y in range(len(x.keys()))])+')', tuple([x[k] for k in x.keys()]))

    def write_stored(self, type, subtype, selection, result):
        pass #TODO

    def commit(self):
        self.connection.commit()

    def unload(self):
        self.cursor.close()
        self.connection.close()

    #-----------------------------------------------------------------------------#   
    def stat_shortcut(self, chara, chr):
        return False
        return 'select max(rowid) from' + chr
