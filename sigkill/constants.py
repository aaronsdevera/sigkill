WINDOWS_CONFIG = 'C:/Users/[USER]/AppData/Roaming/Signal/config.json'
WINDOWS_DB = 'C:/Users/[USER]/AppData/Roaming/Signal/sql/db.sqlite'
DARWIN_CONFIG = '/Users/[USER]/Library/Application Support/Signal/config.json'
DARWIN_DB = '/Users/[USER]/Library/Application Support/Signal/sql/db.sqlite'
LINUX_CONFIG = '/home/[USER]/.config/Signal/config.json'
LINUX_DB = '/home/[USER]/.config/Signal/sql/db.sqlite'

ARTIFACTS_CONFIG = {
    'Windows': {
        'config': WINDOWS_CONFIG,
        'db': WINDOWS_DB
    },
    'Darwin': {
        'config': DARWIN_CONFIG,
        'db': DARWIN_DB
    },
    'Linux': {
        'config': LINUX_CONFIG,
        'db': LINUX_DB
    }
}