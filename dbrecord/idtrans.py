import sqlite3
from .summary import check_db_table_ok


class IDTrans:
    def __init__(self, db_file, table_name, columns):
        opcode, msg = check_db_table_ok(db_file, table_name, columns)
        assert opcode, msg

        self._conn = None
        self._db = None
        self.db_file = db_file
        self.table_name = table_name
        self.columns = columns

    @property
    def conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_file)
        return self._conn

    @property
    def db(self):
        if self._db is None:
            self._db = self.conn.cursor()
        return self._db

    def reconn(self):
        self._conn = None
        self._db = None


class BatchIDSTrans(IDTrans):
    def __call__(self, ids, db_file=None):
        if db_file is not None:
            self.db_file = db_file
            self.reconn()

        if isinstance(ids, int):
            ids = [ids]
        ids_ = ','.join([str(int(i)) for i in ids])

        col = ', '.join(self.columns)
        sql = f'select {col} from {self.table_name} where id in ({ids_})'

        try:
            res = self.db.execute(sql)
        except sqlite3.DatabaseError as e:
            self.reconn()
            return self(ids)

        col = [i[0].lower() for i in res.description]
        ress = res.fetchall()

        mem = {k: list(v) for k, v in zip(col, zip(*ress))}

        return mem
