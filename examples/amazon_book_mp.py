from botflow import *

p_download = Pipe(

    lambda
        p: f"https://www.amazon.com/s/ref=sr_pg_{p}?fst=p90x%3A1&page={p}&rh=n%3A283155%2Ck%3Apython&keywords=python&ie=UTF8&qid=1536500367",
    HttpLoader(),  # download the page

    lambda r: r.soup.find_all("li"),
    Flat()  # we don't need keep the hierarchy of page no.
)

lis=p_download.run(1)

p_get_img_src=Pipe(lambda t:t.select("a img"),lambda t:t['src'])

p_get_title=Pipe(lambda t:t.select("a h2"),lambda t:t.get_text())

p_get_price=Pipe(lambda t:t.select("a > span.a-offscreen"),lambda t:t.get_text())

p_get_price=p_get_price.Map(lambda x:float(x.replace("$",'')))

item_parse=Pipe(Zip(p_get_price,p_get_title,p_get_img_src))


item_parse=Pipe(Zip(p_get_price,p_get_title,p_get_img_src)).Filter(lambda i : i[0])
r=item_parse.run(lis)


import pandas as pd
import matplotlib.pyplot as plt
headers=["price","title","image_src"]
df = pd.DataFrame(r, columns=headers)

print(df)

price=pd.to_numeric(df['price'], errors='coerce')

price.hist()

plt.show()

