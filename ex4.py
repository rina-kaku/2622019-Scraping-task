import requests
from bs4 import BeautifulSoup

url = 'https://www.musashino-u.ac.jp'
res = requests.get(url)

print(f"ステータスコード:{res.status_code}")
print(F"ステータスメッセージ:{res.reason}")

html_soup = BeautifulSoup(res.content, 'html.parser')
print(f"html_soupの型:{type(html_soup)}")

soup_a = html_soup.a
print(soup_a)
print(f"{type(soup_a)}")

soup_p = html_soup.p
print(soup_p)
print(f"{type(soup_p)}")

soup_div = html_soup.div

soup_div_div = soup_div.div
print(soup_div_div)
print(f"{type(soup_div_div)}")

print(f"{soup_a.string}")

print(f"{soup_div_div.string}")