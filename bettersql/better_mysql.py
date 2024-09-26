import mysql.connector
import pandas as pd
from autocomp import Wordcompleter
import getpass
import sys
import os

class SQLEngine:
    
    def __init__(self, host, user, passwd, autocommit):
        
        try:
            self.conn = mysql.connector.connect(
                                                    host = host,
                                                    user = user,
                                                    password = passwd
                                                    )
            if self.conn.is_connected():
                print("bmysql>>Connection successful!")
            else:
                print("bmysql>>Connection failed")
                sys.exit()
        except mysql.connector.Error as err:
            print(f"bmysql>>Connection error: {err}")
            sys.exit()
            
        self.curr = self.conn.cursor()
        self.autocommit = autocommit
        
    def execute(self, query):
        try:
            self.curr.execute(query)
            if query.startswith("select") or query.startswith("show"):
                n = 0
                for row in self.curr.fetchall():
                    print(row)
                print()
            if self.autocommit:
                self.conn.commit()
        except mysql.connector.Error as err:
            print(err)
        
    def commit(self):
        self.conn.commit()
        print("bmysql>>Committed")
        
def main():
    
    mysql_keywords = [
        "accessible", "add", "all", "alter", "analyze", "and", "as", "asc", "asensitive", "before",
        "between", "bigint", "binary", "blob", "both", "by", "call", "cascade", "case", "change", 
        "char", "character", "check", "collate", "column", "condition", "constraint", "continue", 
        "convert", "create", "cross", "cube", "cume_dist", "current_date", "current_time", 
        "current_timestamp", "current_user", "cursor", "database", "databases", "day_hour", 
        "day_microsecond", "day_minute", "day_second", "dec", "decimal", "declare", "default", 
        "delayed", "delete", "dense_rank", "desc", "describe", "deterministic", "distinct", 
        "distinctrow", "div", "double", "drop", "dual", "each", "else", "elseif", "empty", 
        "enclosed", "escaped", "except", "exists", "exit", "explain", "false", "fetch", "first_value", 
        "float", "float4", "float8", "for", "force", "foreign", "from", "fulltext", "function", 
        "generated", "get", "grant", "group", "grouping", "groups", "having", "high_priority", 
        "hour_microsecond", "hour_minute", "hour_second", "if", "ignore", "in", "index", "infile", 
        "inner", "inout", "insensitive", "insert", "int", "int1", "int2", "int3", "int4", "int8", 
        "integer", "interval", "into", "io_after_gtids", "io_before_gtids", "is", "iterate", 
        "join", "json_table", "key", "keys", "kill", "lag", "last_value", "lateral", "lead", "leading", 
        "leave", "left", "like", "limit", "linear", "lines", "load", "localtime", "localtimestamp", 
        "lock", "long", "longblob", "longtext", "loop", "low_priority", "master_bind", "master_ssl_verify_server_cert", 
        "match", "maxvalue", "mediumblob", "mediumint", "mediumtext", "middleint", "minute_microsecond", 
        "minute_second", "mod", "modifies", "natural", "not", "no_write_to_binlog", "nth_value", 
        "ntile", "null", "numeric", "of", "on", "optimize", "optimizer_costs", "option", "optionally", 
        "or", "order", "out", "outer", "outfile", "over", "partition", "percent_rank", "precision", 
        "primary", "procedure", "purge", "range", "rank", "read", "reads", "read_write", "real", 
        "recursive", "references", "regexp", "release", "rename", "repeat", "replace", "require", 
        "resignal", "restrict", "return", "revoke", "right", "rlike", "row", "rows", "row_number", 
        "schema", "schemas", "second_microsecond", "select", "sensitive", "separator", "set", 
        "show", "signal", "smallint", "spatial", "specific", "sql", "sqlexception", "sqlstate", 
        "sqlwarning", "sql_big_result", "sql_calc_found_rows", "sql_small_result", "ssl", "starting", 
        "stored", "straight_join", "system", "table", "tables", "terminated", "then", "tinyblob", "tinyint", 
        "tinytext", "to", "trailing", "trigger", "true", "undo", "union", "unique", "unlock", 
        "unsigned", "update", "usage", "use", "using", "utc_date", "utc_time", "utc_timestamp", 
        "values", "varbinary", "varchar", "varcharacter", "varying", "virtual", "when", "where", 
        "while", "window", "with", "write", "xor", "year_month", "zerofill"
    ]


    
    wc = Wordcompleter(mysql_keywords)
    
    print("BETTER MYSQL")
    print()
    
    host = input("host: ")
    user = input("user: ")
    passwd = getpass.getpass(prompt = "password: ")
    ac = input("Enable autocommit (y/n): ")
    
    if host.strip() == "":
        host = "localhost"
    
    if user.strip() == "":
        user = "root"
        
    if ac.lower().strip() == 'y' or ac.lower().strip() == '':
        ac = True
    else:
        ac = False
    
    sqleng = SQLEngine(host, user, passwd, autocommit = ac)
    
    print()
    
    while True:
        query = wc.prompt(prompt_ = "bmysql>>")
        
        if query.strip() == "":
            continue
        
        if query.lower().strip() == "quit":
            print("Goodbye!")
            break
        
        if query.lower().strip() == "clr":
            os.system('cls')
            continue
        
        if query.endswith(";") == False:
            subq = ""
            while subq.endswith(";") == False:
                subq = wc.prompt(prompt_ = "     ->")
                query = query + subq + " "
                
        query = query.strip(";")

        sqleng.execute(query)

if __name__ == "__main__":
    main()