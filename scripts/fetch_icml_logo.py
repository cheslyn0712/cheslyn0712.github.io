import re
import urllib.request

for url in [
    "https://icml.cc/Conferences/2026/Press",
    "https://icml.cc/",
    "https://icml.cc/Conferences/2026",
]:
    html = urllib.request.urlopen(url).read().decode("utf-8", "replace")
    print("===", url, "===")
    for pat in [
        r'href="([^"]+\.(?:svg|png|jpg))"',
        r'src="([^"]+\.(?:svg|png|jpg))"',
        r'Logo[^"\']*\.(?:svg|png|jpg)',
    ]:
        for m in re.findall(pat, html, re.I):
            print(m)
