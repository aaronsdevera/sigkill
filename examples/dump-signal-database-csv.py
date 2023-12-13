from sigkill import SigKill

# create an instance of SigKill
sk = SigKill()

# print most recent row from the messages table
print(sk.db().table('messages').load().rows[-1])

# get messages between a specific time range
sql = '''select id,
    conversationId,
    received_at,
    body
from messages
where received_at > 1701000000000 
and received_at < 1702000000000
limit 10
'''
result = sk.db().table('messages').get_sql(sql, ['id', 'conversationId' 'received_at', 'body'])
print(result)

# dump all tables (defaults to csv)
sk.dump()