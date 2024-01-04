import mysql.connector
import time
from constants import *


class Connection:
    con = None

    def __init__(self, target):
        if not target[0].isalpha():
            target = "edefuzz_" + target
        self.table = target
        if DATABASE_MYSQL_SOCKET:
            self.con = mysql.connector.connect(
                unix_socket="/var/run/mysqld/mysqld.sock",
                user=DATABASE_MYSQL_USER,
                password=DATABASE_MYSQL_PASS,
                database="edefuzz",
                autocommit=True,
            )
        else:
            self.con = mysql.connector.connect(
                host=DATABASE_MYSQL_HOST,
                user=DATABASE_MYSQL_USER,
                password=DATABASE_MYSQL_PASS,
                database="edefuzz",
                autocommit=True,
            )
        self.create()

    def __del__(self):
        if self.con and self.con.is_connected():
            self.con.close()

    # Database explained
    #   id          INTEGER     An identifier of the record
    #   action      INTEGER     The action taken on the mutant (0 - baseline, 1 - delete, 2 - modify)
    #   datafield   BLOB        The datafield being mutated, leave NULL if action==baseline
    #   value       VARCHAR     The new value used in the mutant, only used when action==modify
    #   html        MEDIUMBLOB  The result HTML page
    #   timestamp   INTEGER     The Unix timestamp that the record was created
    #
    def create(self):
        cur = self.con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS "
            + self.table
            + """ (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            action INTEGER NOT NULL,
            datafield BLOB,
            value VARCHAR(100),
            html MEDIUMBLOB,
            timestamp INTEGER)
            """
        )

    def add_row(self, action, datafield, value, html):
        cur = self.con.cursor()
        stmt = (
            "INSERT INTO "
            + self.table
            + " (action, datafield, value, html, timestamp) VALUES (%s, %s, %s, %s, %s)"
        )
        cur.execute(stmt, (action, datafield, value, html, int(time.time())))

    def get_baseline(self):
        cur = self.con.cursor(buffered=True)
        stmt = "SELECT * FROM " + self.table + " WHERE action=0"
        res = cur.execute(stmt)
        return cur.fetchall()

    def get_result(self):
        cur = self.con.cursor(buffered=True)
        stmt = "SELECT any_value(id),any_value(action),any_value(datafield),any_value(value),any_value(html),any_value(timestamp) FROM " + self.table + " WHERE action<>0 GROUP BY datafield"
        cur.execute(stmt)
        return cur.fetchall()

    def get_record(self, id):
        cur = self.con.cursor(buffered=True)
        stmt = "SELECT html FROM " + self.table + " WHERE id=" + str(id)
        res = cur.execute(stmt)
        return cur.fetchone()[0]

    def record_exist(self, action, datafield, value):
        cur = self.con.cursor(buffered=True)
        res = None
        if value is None:
            res = cur.execute(
                "SELECT count(*) FROM "
                + self.table
                + " WHERE action=%s AND datafield=%s",
                (action, datafield)
            )
        else:
            res = cur.execute(
                "SELECT count(*) FROM "
                + self.table
                + " WHERE action=%s AND datafield=%s AND value=%s",
                (action, datafield, value)
            )

        final = False
        if res:
            final = bool(cur.fetchone())
        return final
    
    def clear(self):
        cur = self.con.cursor(buffered=True)
        cur.execute(
            "DELETE FROM "
            + self.table
            + ";"
        )

if __name__ == "__main__":
    # create()
    # add_row("""["abc", 5, "def", 0, "1", "xyz"]""", 0, None, """<div class="abc "><div><p id='oo'>eeee&nbsp;aa</div>""")
    target = "freepik"
    print(record_exist(1, str(["successs"]), None))
    print(get_baseline("undefined"))
