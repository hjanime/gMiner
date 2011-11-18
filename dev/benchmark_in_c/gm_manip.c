#include <Python.h>
#include <sqlite3.h>

void gm_complement(sqlite3_stmt** ins, sqlite3_stmt** outs){
    int i;
    int count_cols;
    while((count_cols = gm_read_next(ins[0])) > 0){
                                  for(i=0; i<count_cols; i++) {
                                         printf("%s = ", sqlite3_column_name(ins[0], i));
                                         switch(sqlite3_column_type(ins[0], i)) {
                                         case SQLITE_TEXT:
                                                 printf("%s", sqlite3_column_text(ins[0], i));
                                                 break;
                                         case SQLITE_INTEGER:
                                                 printf("%d", sqlite3_column_int(ins[0], i));
                                                 break;
                                         case SQLITE_FLOAT:
                                                 printf("%f", sqlite3_column_double(ins[0], i)); 
                                      }
    if (count_cols==0){return Py_BuildValue("");}
    else {return NULL;}}

void gm_overlap(sqlite3_stmt** ins, sqlite3_stmt** outs){
    return Py_BuildValue("");}

void gm_overlap_pieces(sqlite3_stmt** ins, sqlite3_stmt** outs){
    return Py_BuildValue("");}

void gm_merge(sqlite3_stmt** ins, sqlite3_stmt** outs){
    return Py_BuildValue("");}

/* ------------------------------------------------------------ */
int read_next(sqlite3_stmt stmt){
    switch(sqlite3_step(stmt)) {
       case SQLITE_ROW:  return sqlite3_column_count(stmt);
       case SQLITE_DONE: return 0;
       case SQLITE_BUSY:
          printf("SQL busy error\n");
          return -1;
       case SQLITE_ERROR:
          printf("SQL step error\n");
          return -1;}}

sqlite3* open_database(PyObject* pystring_path){
    /* Prepares the connection to the SQLite database */
    const char* string_path;
    string_path = PyString_AsString(pystring_path);
    sqlite3* db;
    int result;
    result = sqlite3_open(string_path, &db);
    if(result){
        printf("Can't open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return NULL;}
    return db;}

static PyObject* manipulation(PyObject* self, PyObject* args){
    char*     str_ManipName;
    PyObject* pyl_PathsRead;
    int       int_ReadCount;
    PyObject* pyl_PathsWrite;
    int       int_WriteCount;
    char*     str_QueryRead; 
    char*     str_QueryWrite; 
    if (!PyArg_ParseTuple(args, "sOiOis", &str_ManipName, &pyl_PathsRead, &int_ReadCount, &pyl_PathsWrite, &int_WriteCount, \
        &str_QueryRead, &str_QueryWrite)){
        printf("Failed parsing python input\n");
        return NULL;}
    int i;
    int result;
    sqlite3* db;
    /*---------*/
    sqlite3_stmt* stm_Read[int_ReadCount];
    for(i=0; i<int_ReadCount; i++){
        db = open_database(PyList_GetItem(pyl_PathsRead,i))
        if (db==NULL){
            return NULL;}
        result = sqlite3_prepare(db, str_QueryRead, 0, &stm_Read[i], 0);
        if(result!=SQLITE_OK) {
            printf("SQL error in preparing read statement (#%d): %s\n", result, sqlite3_errmsg(db));
            return NULL;}
    /*---------*/
    sqlite3_stmt* stm_Write[int_ReadCount];
    for(i=0; i<int_WriteCount; i++){
        db = open_database(PyList_GetItem(pyl_PathsWrite,i))
        if (db==NULL){
            return NULL;}
        result = sqlite3_prepare(db, str_QueryWrite, 0, &stm_Write[i], 0);
        if(result!=SQLITE_OK) {
            printf("SQL error in preparing write statement (#%d): %s\n", result, sqlite3_errmsg(db));
            return NULL;}
    /*---------*/
    void (*fnpointer_manip)(sqlite3_stmt**, sqlite3_stmt**);
    fnpointer_manip = NULL;
    if(strcmp(str_ManipName, "complement"       )==0){fnpointer_manip = &gm_complement      ;}
    if(strcmp(str_ManipName, "overlap"          )==0){fnpointer_manip = &gm_overlap         ;}
    if(strcmp(str_ManipName, "overlap_pieces"   )==0){fnpointer_manip = &gm_overlap_pieces  ;}
    if(strcmp(str_ManipName, "merge"            )==0){fnpointer_manip = &gm_merge           ;}
    if(fnpointer_manip == NULL){
        printf("Not a correct manipulation name\n");
        return NULL;}
    return (*fnpointer_manip)(stm_Read, stm_Write);}

/* ------------------------------------------------------------ */
static PyMethodDef ModuleMethods[] = {
    /* Declare all the module's functions */
    {"manipulation", manip, METH_VARARGS, "No doc."},
    {NULL, NULL, 0, NULL}};
PyMODINIT_FUNC initgm_manip(void){
    /* Create the module and add the functions */
    (void) Py_InitModule("gm_manip", ModuleMethods);}
