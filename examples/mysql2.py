
from botflow.flow import Pipe,Loop,Fork
from botflow.botframe import BotFrame
from botflow.db.mysql import Query,Insert



dbconf={}
dbconf['host']= '127.0.0.1'
dbconf['port']=3306
dbconf['user']= 'root'
dbconf['password']= 'admin123'
dbconf['db']= 'mysql'

class User(object):
    def __init__(self):
        self.name=None
        self.host=None
        self.user=None

    def __repr__(self):
        return 'class user %s,%s,%s'%(self.name,self.host,self.user)

def main():
    print('ex1----')
    Pipe(

            Loop(range(1)),
            Query('select * from mysql.user limit 10 ', **dbconf, map_class=User),
            Fork(print),
            Insert('insert into jk.new_table(user,host)values ("{user}","{host}")', **dbconf),
        )


    BotFrame.run()




main()




