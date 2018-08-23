
from databot.flow import Pipe,Loop,Fork
from databot.botframe import BotFrame
from databot.db.mysql import Query



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
            print

        )


    BotFrame.run()

    print('ex2----param bind with inout')
    Pipe(

            Loop(range(10)),
            Query('select %s ', **dbconf),
            print

        )


    BotFrame.run()

    print('ex3----param bind with dict')
    u=User()
    u.user='root'
    Pipe(

            Loop([{'user':'root'},u.__dict__]),
            Query('select host,user from mysql.user where user="{user}" ', **dbconf),
            print

        )


    BotFrame.run()


main()




