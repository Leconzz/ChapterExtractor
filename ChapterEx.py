import requests
from bs4 import BeautifulSoup
import re
import time
import os

# --- Config ---
BASE_URL = "https://novelfire.net/book/shadow-slave/chapter-{}"
OUTPUT_DIR = "./chapters"
START_CHAPTER = 3001
END_CHAPTER = 3160  # adjust as needed
DELAY_SECONDS = 2  # be polite to the server

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Known watermark/junk strings to strip from paragraph text
WATERMARK_PATTERNS = [
    r"pᴀɴdᴀ\s*nᴏveʟ",
]

def clean_paragraph_text(text):
    """Remove known watermarks and normalize whitespace."""
    for pattern in WATERMARK_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_chapter(html):
    """Given raw HTML, return (title, list_of_paragraph_html_strings)."""
    soup = BeautifulSoup(html, "html.parser")

    content_div = soup.find("div", id="content")
    if not content_div:
        return None, []

    title_span = soup.find("span", class_="chapter-title")
    # FIX 1: Extract just the plain text for the title string to use in headers/filenames
    title = title_span.get_text(strip=True) if title_span else "Untitled Chapter"
    # print(title[0])
    title = re.sub(r'(\d{4})', r'\1:', title)

    paragraphs = []
    for p in content_div.find_all("p"):
        # Remove stray empty inline tags like <del></del> before extracting text
        for tag in p.find_all(["del", "ins", "sup", "sub"]):
            if not tag.get_text(strip=True):
                tag.decompose()

        # FIX 2: Clean the internal text content *inside* the <p> tag without dropping the tag
        cleaned_text = clean_paragraph_text(p.get_text())
        p.string = cleaned_text

        # FIX 3: Check if the text is empty. If it has text, append the whole tag as a string
        if cleaned_text:  
            paragraphs.append(str(p))

    return title, paragraphs


def save_chapter(chapter_num, title, paragraphs, output_dir):
    save_chapter.count += 1
    os.makedirs(output_dir, exist_ok=True)
    # FIX 4: Changed file extension to .html since it now contains tags
    filepath = os.path.join(output_dir, f"{save_chapter.count:03d}_{chapter_num:04d}_{title}.xhtml")

    with open(filepath, "w", encoding="utf-8") as f:
        # Optional: Added basic HTML wrappers so it opens nicely in a browser
        f.write(f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n<head>\n<title>{title}</title>\n<link href="Styles/stylesheet.css" type="text/css" rel="stylesheet"/>\n</head>\n<body>\n')
        f.write(f"<h1>{title}</h1>\n")
        for para in paragraphs:
            f.write(para + "\n")
        f.write("\n</body></html>")

    print(f"Saved: {filepath}")

save_chapter.count = 0
def scrape_range(start, end):
    for chapter_num in range(start, end + 1):
        url = BASE_URL.format(chapter_num)
        print(f"Fetching {url} ...")

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch chapter {chapter_num}: {e}")
            continue

        title, paragraphs = extract_chapter(response.text)

        if not paragraphs:
            print(f"No content found for chapter {chapter_num}, skipping.")
            continue

        save_chapter(chapter_num, title, paragraphs, OUTPUT_DIR)

        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    scrape_range(START_CHAPTER, END_CHAPTER)
