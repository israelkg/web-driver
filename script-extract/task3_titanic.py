"""
Task 3 - Baixar dataset Titanic usando Playwright + BeautifulSoup.

Fonte: https://github.com/datasciencedojo/datasets/blob/master/titanic.csv
"""

import csv
import io
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BLOB_URL = "https://github.com/datasciencedojo/datasets/blob/master/titanic.csv"
OUTPUT_CSV = Path(__file__).parent.parent / "dados" / "titanic.csv"


def baixar_titanic() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"Abrindo {BLOB_URL}")
        page.goto(BLOB_URL, wait_until="domcontentloaded")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        raw_link = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/raw/" in href and href.endswith("titanic.csv"):
                raw_link = href
                break

        if raw_link is None:
            raw_link = "/datasciencedojo/datasets/raw/master/titanic.csv"
            print("Link raw nao achado no HTML, usando fallback.")

        if raw_link.startswith("/"):
            raw_link = "https://github.com" + raw_link

        print(f"Baixando CSV de {raw_link}")
        response = page.request.get(raw_link)
        if not response.ok:
            raise RuntimeError(f"Falha download: status {response.status}")

        csv_text = response.text()
        OUTPUT_CSV.write_text(csv_text, encoding="utf-8")
        print(f"Salvo em {OUTPUT_CSV}")

        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        header, data = rows[0], rows[1:]
        print(f"Colunas: {header}")
        print(f"Total linhas: {len(data)}")
        print("Primeiras 5 linhas:")
        for row in data[:5]:
            print(row)

        browser.close()


if __name__ == "__main__":
    baixar_titanic()
