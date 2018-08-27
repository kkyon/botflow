from databot.flow import Pipe,Timer
from databot.botframe import BotFrame
from databot.http.http import HttpLoader


def main():
    Pipe(

        Timer(delay=2,max_time=5),
        "http://api.coindesk.com/v1/bpi/currentprice.json",
        HttpLoader(),
        lambda r:r.json['bpi']['USD']['rate_float'],
        print,
    )

    BotFrame.render('simple_bitcoin_price')
    BotFrame.run()

main()
