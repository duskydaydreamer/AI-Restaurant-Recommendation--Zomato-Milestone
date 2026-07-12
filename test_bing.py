import urllib.parse, urllib.request, json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def test_query(q):
    url = f"https://tse1.mm.bing.net/th?q={urllib.parse.quote(q)}"
    print(f"Query: {q}")
    print(f"URL: {url}")
    # We can't easily see the image, but we can verify it doesn't 404
    req = urllib.request.Request(url, method="HEAD")
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        print(f"Status: {resp.status}")
    except Exception as e:
        print(f"Error: {e}")

test_query("Bombay Brasserie restaurant Bangalore interior architecture -people")
test_query("Bombay Brasserie restaurant Bangalore interior architecture -people -site:zomato.com -site:eazydiner.com")
