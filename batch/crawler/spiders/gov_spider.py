import scrapy
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urlparse
from functions import pred
import scrape
from fake_headers import Headers


class govSpider(scrapy.Spider):
    name = "mygovscraper"
    max_retries = 2
    allowed_domains = []
    start_urls = []
    nations_dict = {}
    headergen = Headers(headers=True)
    english = [
        "en",
        "english",
        "eng",
        "engl",
        "angles",
        "anglictina",
        "engelsk",
        "inglise",
        "anglais",
        "ingles",
        "ingilizce",
        "engelsk",
        "anglictina",
        "engleza",
        "engelsk",
        "inggeris",
        "inggris",
        "englisch",
        "engels",
        "engleski",
        "angla",
        "englanti",
        "anglu",
        "angielski",
        "engels",
        "chingerezi",
        "inggris",
        "enska",
        "ingarihi",
        "igilisi",
        "parenglish",
    ]  # stay in english domains
    banned = [
        "state",
        "how",
        "map",
        "pdf",
        "program",
        "news",
        "press",
        "topic",
        "service",
        "application",
        "employment",
        "immigration",
        "law",
        "public-health",
        "symbol",
        "function",
        "environment",
        "current-affairs",
        "policy",
        "resource",
        "previous",
        "mission",
        "work",
        "procure",
        "alert",
        "notice",
        "guidance",
        "foreign",
        "catalogue",
        "life",
        "past",
        "people",
        "search",
        "docs",
        "cookies",
        "interview",
        "actual",
        "publication",
        "document",
        "action",
        "decision",
        "gallery",
        "museum",
        "society",
        "culture",
        "foto",
        "landmark",
        "develop",
        "publish",
        "support",
        "business",
        "announcement",
        "activ",
        "archive",
        "article",
        "guideline",
        "practice",
        "procedure",
        "chapter",
        "scheme",
        "report",
        "spotlight",
        "feedback",
        "speech",
        "blog",
        "faq",
        "covid",
        "question",
        "statement",
        "permit",
        "travel",
        "living",
        "apply",
        "essence",
        "advert",
        "interest",
        "tax",
        "budget",
        "bill",
        "node",
        "taxonomy",
        "event",
        "health-canada",
        "gazette",
        "classified",
        "compilation",
        "document",
        "dokument",
        "stats",
        "contact",
        "default",
        "issue",
        "agenda",
        "history",
        "visit",
        "theme",
        "tour",
        "technology",
        "glance",
        "browse",
        "debate",
        "rules",
        "involved",
        "policies",
        "countries",
        "design",
        "campaign",
        "consult",
        "sport",
        "corporate",
        "revenue",
        "heritage",
        "child",
        "journal",
        "portail",
        "story",
        "order",
        "photo",
        "statistics",
        "drug",
    ]  # media,premier  #global stop words not to be crawled
    redirected = []

    def __init__(self, filename="rss.csv", *args, **kwargs):
        super(govSpider, self).__init__(*args, **kwargs)
        self.retries = {}
        nations = pd.read_csv(filename, encoding="unicode_escape")

        if nations.isnull().any().any():
            pre = len(nations)
            nations.dropna(axis=0, how="any", inplace=True)
            print(f"Excluding {pre-len(nations)} NaN row(s) from {filename}")

        for i in range(len(nations)):
            site = nations.iloc[i, 0].strip()
            self.start_urls.append(site)
            for item in self.english:
                if item in site.lower().split("/"):
                    self.nations_dict[self.ret_domain(site)] = (
                        nations.iloc[i, 1].strip(),
                        "en",
                    )
                    break
            else:
                self.nations_dict[self.ret_domain(site)] = (
                    nations.iloc[i, 1].strip(),
                    None,
                )

            self.allowed_domains.append(
                urlparse(site).netloc
            )  # keeps crawler within given domain
        print(
            f"Crawler has started crawling with {len(self.start_urls)} inital site(s). Please wait for timeout or press ctrl+c repeatedly to force stop."
        )

    def ret_domain(self, site):  # to get root domain of response url
        domain = urlparse(site).netloc
        if domain[:4] == "www.":
            return domain[4:]
        return domain

    def ret_nation(self, domain):  # to extract nation from response url
        if len(domain) == 0:
            return 0
        if domain in self.nations_dict.keys():
            return self.nations_dict[domain][0]
        else:
            if len(domain.split(".", 1)) == 1:
                return 0
            return self.ret_nation(domain.split(".", 1)[1])

    def start_requests(self):  # scrapy initiation function
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"handle_httpstatus_list": [302, 307]},
                headers=self.headergen.generate(),
            )

    def parse(self, response):
        if response.status == 302 or response.status == 307:
            retries = self.retries.setdefault(response.url, 0)
            if retries < self.max_retries:
                self.retries[response.url] += 1
                yield response.request.replace(dont_filter=True)
            else:
                self.logger.error(
                    "%s still returns 302 responses after %s retries",
                    response.url,
                    retries,
                )
            return

        # self.logger.info("Scraped %s", response.url)
        f = open("log.txt", "a")
        f.write("Scraped {}\n".format(response.url))
        f.close()

        # print('soup object is created')
        soup = BeautifulSoup(response.text, "html.parser")
        domain = self.ret_domain(response.url)
        nation = self.ret_nation(domain)
        # for item in self.banned:                #filtering stopwords for 1st visit
        # if item in response.url.lower():
        # break
        # else:
        # scrape.parse_soup(domain,nation,response.url,soup)

        scrape.parse_soup(domain, nation, response.url, soup)

        # for href in soup.find_all('a'):
        # try:
        # raw = href["href"]
        # tag = href.text
        # except:
        # continue
        # if len(raw)==0 or 'javascript' in raw:
        # continue

        # if(raw[0].isalpha() or raw[0]=='/'):     #to scrape valid websites only
        # new = response.urljoin(raw)
        # flag=0
        # if(pred(tag)) and (tag not in self.redirected):    #crawler intelligence

        # if self.nations_dict[domain][1] == 'en':
        # for item in self.english:
        # if item in new.lower().split('/'):
        # flag=1
        # elif self.nations_dict[domain][1] is None:
        # flag=1

        # for item in self.banned:  #filtering stopwords for found urls
        # if item in raw.lower():
        # break

        # else:
        # if flag==1: #do not scrape other languages
        # self.redirected.append(tag)
        # yield scrapy.Request(new, self.parse, meta={'handle_httpstatus_list': [302, 307]}, headers = self.headergen.generate())
