import os
import pwd
import time
import logging

from sigkill.lib import SignalDatabase
from sigkill.constants import ARTIFACTS_CONFIG

class SigKill():
    '''
    class for sigkill
    '''
    logger: logging.Logger = None
    user: str = None
    os: str = None
    os_artifacts: dict = None
    config_filepath: str = None
    db_filepath: str = None
    db: SignalDatabase = None

    def __init__(self, signal_artifacts_config: dict = ARTIFACTS_CONFIG):
        '''
        constructor
        '''
        self.logger = logging.getLogger(__name__)
        self.user = self.detect_user()
        self.os = self.detect_os()
        self.os_artifacts = self.get_os_artifacts(signal_artifacts_config)
        self.config_filepath = self.get_os_config_filepath()
        self.db_filepath = self.get_os_db_filepath()
        self.sdb = SignalDatabase(
            config_filepath=self.config_filepath,
            db_filepath=self.db_filepath,
            logger=self.logger
        )
    
    def detect_user(self):
        '''
        method for detecting the current user
        '''
        return pwd.getpwuid(os.getuid())[0]
    
    def detect_os(self):
        '''
        method for detecting the current os
        '''
        return os.uname().sysname
    
    def get_os_artifacts(self, signal_artifacts_config: dict):
        '''
        method for getting the os-specific artifacts
        '''
        return signal_artifacts_config[self.os]
    
    def get_os_config_filepath(self):
        '''
        method for getting the os-specific config filepath
        '''
        return self.os_artifacts['config'].replace('[USER]',self.user)
    
    def get_os_db_filepath(self):
        '''
        method for getting the os-specific db
        '''
        return self.os_artifacts['db'].replace('[USER]',self.user)

    def db(self):
        '''
        method for getting the SignalDatabase object
        '''
        return self.sdb
    
    def dump(self, output_directory: str = None, output: str = 'csv'):
        '''
        method for dumping all tables from the SignalDatabase object
        '''
        start_ts = time.time()
        TARGET_DIR = output_directory
        if TARGET_DIR is None:
            TARGET_DIR = 'sigkill-dump-' + str(int(start_ts))
        os.makedirs(TARGET_DIR, exist_ok=True)
        for table in self.db().get_tables():
            table_result = table.load()
            if table.status != 'success':
                self.logger.error(f'[-] skipping "{table.name}" due to error')
                continue
            if table.fields:
                self.logger.debug(f'[+] dumping "{table.name}" with fields {",".join(table.fields)}')
            if table_result:
                if output.lower() == 'csv':
                    table_result.to_csv(f'{TARGET_DIR}/{table.name}.{output.lower()}')
                elif output.lower() == 'json':
                    table_result.to_json(f'{TARGET_DIR}/{table.name}.{output.lower()}')
        end_ts = time.time()
        return {'status': 'success', 'msg': f'dumped to {TARGET_DIR}', 'time': end_ts - start_ts}
    
