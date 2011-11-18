# For the python module type:
# $ python setup.py build

# For the C executable type:
# $ gcc -pthread -fno-strict-aliasing -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fPIC -I/usr/local/include -I/usr/include/python2.6 -c gm_manip.c -o gm_manip.o  
# $ gcc -pthread gm_manip.o -L/usr/lib64 -lpython2.6 -lsqlite3 -o gm_manip

from distutils.core import setup, Extension
module = Extension( 'gm_manip',
                    sources = ['gm_manip.c'],
                    include_dirs = ['/usr/local/include'],
                    libraries = ['sqlite3']
                  )

setup (name = 'gm Manipulations in C',
       version = '0.1',
       description = 'No description',
       ext_modules = [module])
