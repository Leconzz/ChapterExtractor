# import requests
# from bs4 import BeautifulSoup
# import re
# import time
# import os

# # --- Config ---
# url = "https://novelfire.net/book/shadow-slave/chapter-3001"
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
# }

# response = requests.get(url, headers=HEADERS, timeout=15)

# html = response.text

# soup = BeautifulSoup(html, "html.parser")

# title_div = soup.find("span", class_="chapter-title")

# title = title_div.get_text(strip=True) if title_div else "Untitled Chapter"

# print(title)
import re

title = ['Chapter 3139 Effie is Coming, Shut the Gates!']
title_str = title[0]
new_title = re.sub(r'(\d{4})', r'\1:', title_str)
print(new_title)