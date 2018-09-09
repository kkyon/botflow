from botflow import *
from botflow.config import config
config.exception_policy=config.Exception_ignore


Pipe(
    range(10),
    lambda p:f"https://www.amazon.com/s/ref=sr_pg_{p}?fst=p90x%3A1&page={p}&rh=n%3A283155%2Ck%3Apython&keywords=python&ie=UTF8&qid=1536500367",
    HttpLoader(),

    #lambda r:r.soup.get_all_links(),
    lambda r:r.soup.select("a h2"),
    lambda r:r.get_text(),
    AioFile("ex_output/amazon_book.csv")

)

Bot.run()



fetch("https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false", {"credentials":"include","headers":{},"referrer":"https://www.lagou.com/jobs/list_python?px=default&city=%E5%8C%97%E4%BA%AC","referrerPolicy":"no-referrer-when-downgrade","body":"first=false&pn=2&kd=python","method":"POST","mode":"cors"});