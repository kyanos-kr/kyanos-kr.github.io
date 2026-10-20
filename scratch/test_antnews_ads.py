import urllib.request
import re

url = "https://www.antnews.org"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8", errors="ignore")

# Look for real article links (e.g. .html or query params)
links = set(re.findall(r'href="([^"]+)"', html))
real_articles = [l for l in links if any(k in l for k in ["/news/", "/view/", "idx=", "art_", "article", "b_code"])]
print("Real articles count:", len(real_articles))
for a in real_articles[:5]:
    print("Article link:", a)
    target = a if a.startswith("http") else ("https://www.antnews.org" + a if a.startswith("/") else "https://www.antnews.org/" + a)
    try:
        art_req = urllib.request.Request(target, headers=headers)
        with urllib.request.urlopen(art_req) as art_resp:
            art_html = art_resp.read().decode("utf-8", errors="ignore")
            print(" -> Script present:", "pagead2.googlesyndication.com" in art_html)
            print(" -> ins count:", art_html.count("<ins"))
            print(" -> adsbygoogle.push count:", art_html.count("adsbygoogle.push"))
    except Exception as e:
        print(" -> Error:", e)
