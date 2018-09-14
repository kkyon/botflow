from botflow import *


def main():
    Pipe(

        Timer(delay=2,max_time=10),  # send timer data to pipe every 2 seconds
        "http://api.coindesk.com/v1/bpi/currentprice.json",  # send url to pipe when timer trigger
        HttpLoader(),  # read url and load http response
        lambda r: r.json['bpi']['USD']['rate_float'],  # read http response and parse as json
        print,  # print out

    )

    Bot.render('ex_output/simple_bitcoin_price')
    Bot.run()
# main()
print('-----chian style----')
from botflow import *

p_cd_bitcoin = Pipe().Timer(delay=2,max_time=10).Loop("http://api.coindesk.com/v1/bpi/currentprice.json") \
    .HttpLoader().Map(lambda r: r.json['bpi']['USD']['rate_float']).Map(print)

p_cd_bitcoin.run()
print('--run twinice---')
p_cd_bitcoin.run()