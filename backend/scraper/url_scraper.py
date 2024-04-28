import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver

# use Selenium to scrape webpages with dynamically rendered content
async def scrape_url_with_selenium(url):

    # initialize Chrome WebDriver
    browser = webdriver.Chrome()
    browser.get(url)

    # allow time dynamic content to load
    await asyncio.sleep(30)
    html_content =  browser.page_source
    return html_content

# find titles, authors, and texts from content
async def scrape_url(url):

    # implemented scraper using Zyte API (could not scrape dynamically rendered webpages)
    # client = AsyncZyteAPI(api_key=api_key)
    # response = await client.get({"url": url, "httpResponseBody": True})
    # html_content = b64decode(response["httpResponseBody"]).decode()

    # scrape and parse the HTML content
    html_content = await scrape_url_with_selenium(url)
    soup = BeautifulSoup(html_content, "html.parser")

    # extract title and text
    title = soup.title.text.strip() if soup.title else None
    text = soup.get_text(strip=True)[:35000] # only extract first 35000 characters stay under OpenAI token limit

    # scrape authors from Ash Publications
    authors = [author.text.strip() for author in soup.find_all("a", class_="linked-name js-linked-name stats-author-info-trigger")]
    
    # scrape authors from SEC filing
    if authors == []:
        authors = [author.text.strip() for author in soup.find_all(lambda tag: tag.name == "ix:nonnumeric" and tag.get("name") == "dei:EntityRegistrantName")]
    
    # scrape authors from Abstracts Online
    if authors == []:
        authors_tag = soup.find("dt", string="Disclosures")
        if authors_tag:
            dd_tag = authors_tag.find_next_sibling("dd")
            if dd_tag:
                for bold_tag in dd_tag.find_all("b"):
                    author_name = bold_tag.text.strip()
                    if author_name and author_name[-1] == ",":
                        authors.append(author_name[:-1])

    return {"url": url, "title": title, "text": text, "authors": authors}