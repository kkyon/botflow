from botflow import *

p = Pipe(
    range(3),
    lambda
        p: f"https://www.amazon.com/s/ref=sr_pg_{p}?fst=p90x%3A1&page={p}&rh=n%3A283155%2Ck%3Apython&keywords=python&ie=UTF8&qid=1536500367",
    HttpLoader(),

    lambda r: r.soup.find_all("li"),
    Flat()
)

links = p.run(0)

print(links)
#li=Pipe(links).Flat().run()