import json
import os.path
import sqlite3


TODO_SQL_DB = "todos.db"


def execute_query(db, query, commit=False, return_value=False):
    con = sqlite3.connect(db)
    cur = con.cursor()
    result = cur.execute(query)
    if return_value:
        rows = result.fetchall()
    if commit:
        con.commit()
    con.close()
    if return_value:
        return rows
