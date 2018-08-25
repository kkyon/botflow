import asyncio
from aiomysql import create_pool,cursors
from databot.node import Node
import pymysql
#it may need a executor implemention in future
#close by count ref
import logging
class Mysql(Node):

    def init_param(self):
        self.pool=None
        self.inited=False
        self.closed=False



    async def init(self):


        loop = asyncio.get_event_loop()
        self.sql=self.args[0]
        self.pool=await  create_pool(host=self.kwargs.host, port=self.kwargs.port,
                               user=self.kwargs.user, password=self.kwargs.password,
                               db=self.kwargs.db, loop=loop,cursorclass=cursors.DictCursor)
        self.inited=True

    async def close(self):


        self.pool.close()
        await self.pool.wait_closed()



    def map_to_class(self,d):
        if 'map_class' not in self.kwargs:
            return d
        if not isinstance(d,list):
            d=[d]
        result=[]
        for item in d:
            o=self.kwargs.map_class()
            for k,v in item.items():
                k=k.lower()
                if k in o.__dict__:
                    o.__dict__[k]=v
            result.append(o)

        return result

    def sql_format(self, param):
        if isinstance(param, dict):
            sql = self.sql.format(**param)
        elif hasattr(param, '__dict__') and len(param.__dict__) !=0 :
            try:
                sql = self.sql.format(**param.__dict__)
            except Exception:
                pass
        elif '%s' in self.sql:
            sql = self.sql % (param)
        else:
            sql = self.sql
        return sql
class Query(Mysql):





    async def __call__(self, param):
        sql = self.sql_format(param)
        async with self.pool.get() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                r = await cur.fetchall()
                #TO change it into gen style
                return self.map_to_class(r)



#TODO batch commit
class Insert(Mysql):

    async  def __call__(self, param):


        sql = self.sql_format(param)
        async with self.pool.get() as conn:
            async with conn.cursor() as cur:
                logging.debug(sql)
                r = await cur.execute(sql)
                await conn.commit()
                return r
