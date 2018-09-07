from botflow import *


def main():
    Pipe(

        Timer(delay=2),  # send timer data to pipe every 2 seconds
        "http://api.coindesk.com/v1/bpi/currentprice.json",  # send url to pipe when timer trigger
        HttpLoader(),  # read url and load http response
        lambda r: r.json['bpi']['USD']['rate_float'],  # read http response and parse as json
        print,  # print out

    )

    Bot.render('ex_output/simple_bitcoin_price')
    Bot.run()
main()
