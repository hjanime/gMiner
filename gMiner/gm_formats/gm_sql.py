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
        if selection['type'] == 'chr':
            chr = selection['chr']
            if chr not in self.all_tables: return ()
            cmd = "select " + ','.join(fields) + " from '" + chr + "'"
        if selection['type'] == 'span':
            span = selection['span']
            chr = span['chr']
            if chr not in self.all_tables: return ()
            condition = "start < " + str(span['end']) + " and " + "end > " + str(span['start'])
            cmd = "select " + ','.join(fields) + " from '" + chr + "' where " + condition
        return self.cursor.execute(cmd + ' order by start,end') 

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

    def write_data_quan(self, chr, iterable, fields):
        if chr in [x[0] for x in self.cursor.execute("select name from sqlite_master where type='table'").fetchall()]:
            self.cursor.execute("drop table " + chr)
        self.cursor.execute('create table "' + chr + '" (start integer, end integer, score real)')
        self.cursor.executemany('insert into "' + chr + '"  values (?,?,?)', iterable)
        self.connection.commit()

    def write_meta_data(self, data):
        for k in data.keys(): self.cursor.execute('insert into attributes (key,value) values (?,?)',(k,data[k]))

    def write_chr_meta(self, data):
        # data = [{u'length': 197195432, u'name': u'chr1'},
        #         {u'length': 129993255, u'name': u'chr2'}]
        for x in data: self.cursor.execute('insert into chrNames (' + ','.join(x.keys()) + ') values (' + ','.join(['?' for y in range(len(x.keys()))])+')', tuple([x[k] for k in x.keys()]))
        self.connection.commit()

    def write_stored(self, type, subtype, selection, result):
        pass #TODO

    def commit(self):
        self.connection.commit()

    def make_indexes(self):
        self.refresh_table_list()
        for chr in [x for x in self.all_tables if x != 'attributes' and x != 'chrNames']:
            self.cursor.execute(    "create index '" + chr + "_range_idx' on '" + chr + "' (start,end)")
            fields = [x[1] for x in self.cursor.execute('pragma table_info("'+  chr + '")').fetchall()]
            if 'score' in fields:
                self.cursor.execute("create index '" + chr + "_score_idx' on '" + chr + "' (score)")
            if 'name' in fields:
                self.cursor.execute("create index '" + chr + "_name_idx' on '" +  chr + "' (name)")
        self.connection.commit()
                
    def unload(self):
        self.make_indexes()
        self.cursor.close()
        self.connection.close()

    #-----------------------------------------------------------------------------#   
    def stat_shortcut(self, chara, chr):
        return False
        return 'select max(rowid) from' + chr

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
