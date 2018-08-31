from databot import Pipe,Timer,BotFrame,HttpLoader,Bot

def main():
    Pipe(

        Timer(delay=2,max_time=5),
        "http://api.coindesk.com/v1/bpi/currentprice.json",
        HttpLoader(),
        lambda r:r.json['bpi']['USD']['rate_float'],
        print,
    )

    Bot.render('ex_output/simple_bitcoin_price')
    Bot.run()

main()
