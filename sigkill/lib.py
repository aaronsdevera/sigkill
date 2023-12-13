
import json
import pandas as pd
from numpy import nan as np_nan
import logging
from pysqlcipher3 import dbapi2 as sqlcipher

class SignalDatabase():

    user: str = None
    os: str = None
    config: dict = None
    db: str = None
    key: str = None
    ctx: sqlcipher.Connection = None
    cursor: sqlcipher.Cursor = None
    tables_metadata: list = None
    tables: list = None
    logger: logging.Logger = None

    def __init__(self, config_filepath: str, db_filepath: str, logger: logging.Logger = None):
        '''
        init method for SignalDatabase
        - signal_artifacts_config: dict value from sigkill/constants.py
        '''
        self.logger = logger if logger else logging.getLogger(__name__)
        self.config = self.get_os_config(config_filepath)
        self.key = self.config['key']
        self.ctx = sqlcipher.connect(db_filepath)
        self.cursor = self.ctx.cursor()
        result_decryption = self.decrypt_db()
        if result_decryption['status'] == 'failure':
            raise ValueError(f'[!] {result_decryption["msg"]}')
        self.tables_metadata = self.get_tables_metadata()

    def get_os_config(self, config_filepath):
        '''
        method for loading the os-specific config
        '''
        return json.load(open(config_filepath))

    def execute_sql(self, sql: str):
        '''
        method for executing sql
        '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def decrypt_db(self):
        '''
        method for decrypting the db
        '''
        msg = self.execute_sql(f'PRAGMA key = "x\'{self.key}\'"')[0][0]
        status = 'success' if msg == 'ok' else 'failure'
        return {'status': status, 'msg': msg}
    
    def get_tables_metadata(self):
        '''
        method for getting the sqlite_master for tables in the db
        '''
        return SignalDatabaseTable(cursor=self.cursor, table_name='sqlite_master', logger=self.logger).load()
    
    def get_table_names(self):
        '''
        method for getting all table names in the db
        '''
        return [row['name'] for row in self.tables_metadata.rows if row['type'] == 'table']
    
    def table(self, table_name: str):
        '''
        method for getting a table
        '''
        return SignalDatabaseTable(cursor=self.cursor, table_name=table_name, logger=self.logger)
                                   
    def get_tables(self):
        '''
        method for laoding all tables in the db
        '''
        table_names = self.get_table_names()
        for table_name in table_names:
            yield SignalDatabaseTable(cursor=self.cursor, table_name=table_name, logger=self.logger)

class SignalDatabaseTable():

    logger: logging.Logger = None
    cursor: sqlcipher.Cursor = None
    name: str = None
    fields: list = None
    rows: list = None
    status: str = 'failure'

    def __init__(self, cursor: sqlcipher.Cursor, table_name: str, logger: logging.Logger = None):
        '''
        constructor
        '''
        self.logger = logger if logger else logging.getLogger(__name__)
        self.cursor = cursor
        self.name = table_name
        self.fields = self.get_table_fields()

    def execute_sql(self, sql: str):
        '''
        method for executing sql
        '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_table_fields(self):
        '''
        method for getting all fields in a table
        '''
        try:
            sql = f'PRAGMA table_info({self.name})'
            result = self.execute_sql(sql)
            return [field[1] for field in result]
        except sqlcipher.OperationalError:
            #self.logger.error(f'error getting fields for table "{self.name}"')
            pass
    
    def get_sql(self, sql: str, fields: list = None):
        '''
        method for getting all rows in a table as a list of dicts
        '''
        use_fields = fields if fields else self.fields
        result = self.execute_sql(sql)
        return SignalDatabaseTableResult(
            sql=sql,
            results=result,
            columns=use_fields,
            status='success'
        )
        
    def get_table(self, fields: list = None):
        '''
        method for getting all rows in a table as a list of dicts
        '''
        use_fields = fields if fields else self.fields
        if use_fields:
            sql = f'SELECT {",".join(use_fields)} FROM {self.name}'
            if 'order' in use_fields:
                sql = sql.replace('order', '"order"')
            return SignalDatabaseTableResult(
                sql=sql,
                results=self.execute_sql(sql),
                columns=use_fields,
                status='success'
            )
    
    def load(self):
        '''
        method for loading a table
        '''
        try:
            self.fields = self.get_table_fields()
            self.status = 'success'
        except sqlcipher.OperationalError as e:
            pass
        try:
            return self.get_table()
        except sqlcipher.OperationalError as e:
            pass
    
class SignalDatabaseTableResult():
    sql: str = None
    result: list = None
    rows: list = None
    columns: list = None
    status: str = None

    def __init__(self, sql: str, results: list, columns: list, status: str):
        '''
        constructor
        '''
        self.status = status
        self.sql = sql
        self.results = results
        self.columns = columns
        self.rows = [dict(zip(self.columns, result)) for result in self.results]

    def result(self):
        '''
        method for getting the result
        '''
        return self.rows

    def to_df(self):
        '''
        method for converting a table to a pandas dataframe
        '''
        if self.status == 'failure':
            raise ValueError('[!] table not loaded')
        return pd.DataFrame(self.rows).dropna(axis=1, how='any')
    
    def to_csv(self, filepath: str = None, index: bool = False):
        '''
        method for converting a table to a csv
        '''
        return self.to_df().to_csv(filepath, index=index)
    
    def to_json(self, filepath: str = None, orient: str = 'records'):
        '''
        method for converting a table to a json
        '''
        return self.to_df().replace(to_replace=np_nan, value=None).to_json(filepath, orient=orient)
    
    def __repr__(self):
        return self.to_json()