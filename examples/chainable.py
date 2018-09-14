import logging
logging.basicConfig(level=logging.DEBUG)
from botflow import *
from botflow.config import config
config.exception_policy=config.Exception_pipein

p=Pipe(
    range(1),
    lambda p:f"https://www.amazon.com/s/ref=sr_pg_{p}?fst=p90x%3A1&page={p}&rh=n%3A283155%2Ck%3Apython&keywords=python&ie=UTF8&qid=1536500367",
    HttpLoader(),

    lambda r:r.soup.find_all("li"),
    Flat()
)

links=p.run(0)
print(len(links))
p_get_img_src=Pipe(lambda t:t.select("a img"),lambda t:t['src'])

p_get_title=Pipe(lambda t:t.select("a h2"),lambda t:t.get_text())
p_get_price=Pipe(lambda t:t.select("a > span.a-offscreen"),lambda t:t.get_text())

item_parse=Pipe(Zip(p_get_price,p_get_title,p_get_img_src)).Filter(lambda i : i[0])




r=item_parse.run(links)
print(r)
print(len(r))