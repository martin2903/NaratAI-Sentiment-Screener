import requests
from datetime import datetime
from bs4 import BeautifulSoup

current_date = datetime.now()


def get_stock_news(ticker):
    """A function that retrieves the news articles headlines and urls for a given stock using its ticker by scraping the finviz news feed
       The function works only for the finviz website. Constraints are applied to consider only news for a given day and news that
       are relevant for the given stock ticker(see _check_day and _check_headline_relevancy for more context).

       Params:
       ticker: str - The stock's ticker

       Returns:
       news: dictionary - A dictionary containing the news headlines and their urls
       """

    news={}

    url = 'https://finviz.com/quote.ashx?t={}'.format(ticker)

    # Headers are needed when making the GET request
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)

    # Instantiate the BeutifulSoup scraper
    soup = BeautifulSoup(resp.content, 'html.parser')

    # All articles are contained in an html table with id: news-table
    news_table = soup.find(id='news-table')

    # Each article is contained in an html table row (tr)
    for article in news_table.find_all('tr'):

        # A boolean condition that will terminate the loop when all articles for the given day are scraped
        if _check_date(article):
            # Get the news headline contained in the anchor tag and check if it is relevant for the given stock ticker
            headline = article.find('a').text
            if _check_headline_relevancy(headline,ticker):
                # Get the attribute href that contains the url in each anchor tag (a)
                link = article.find('a', href=True)['href']
                news[headline]=link

        else:
            break

    return news



def _check_date(article_container):
    """"A function that checks whether a table row(tr) containing an article is for the date required.
        The first td element of each tr contains a timestamp. The timestamp is parsed to a datetime object
        and compared to day_today. Only the first element of the table rows containing articles  for a given day in the finviz news-table
        has a timestamp containing the date as well. Therefore, when parsing only the first element is expected to be correctly parsed into a datetime object.
        The next element that does not throw an exception would indicate the end of the section of articles for the given day.
        (Check get_news for context)

        Params:
        article_container: bs4.element.Tag - a table row(tr) element containing the article

        Returns:
        boolean: True if the td element contains today's date. False if it contains another date.
        """

    str_date = article_container.find('td').text[0:9]

    try:
        date = datetime.strptime(str_date, "%b-%d-%y")
        if date.month==current_date.month and date.day ==current_date.day:
            return True
        else:
            return False
    except:
        return True

def _check_headline_relevancy(headline,ticker):
    """A function that checks whether a headline contains words that are relevant to the stock ticker searched.
       The need for it stems from the fact that finviz often has news listed for a given stock that appear to be irrelevant for it.
       A list of search words for each ticker was created and a given headline is considered relevant for a given ticker
       if it contains one of them.

       Params:
       headline: str - The news article headline
       ticker: str - The stock ticker searched

       Returns:
       boolean: True if the headline contains one of the relevant words. False otherwise.
       """

    words = {'TSLA': ['tesla', 'elon', 'musk','tsla'],
             'AMZN': ["amazon", 'bezos', 'amzn', 'aws'],
             'GOOG': ['google','youTube', 'sundar', 'pichai','goog'],
             'HOOD': ['robinhood', 'hood', 'vlad', 'tenev'],
             'NFLX': ['netflix', 'nflx', 'reed', 'hastings'],
             'AAPL': ['apple','aapl','iphone', 'macbook', 'ipad',
                      'airpods', 'cook', 'tim'],
             'FB':['facebook','mark','zuckerberg','instagram','social','fb','whatsapp', 'meta','metaverse'],
             'AMC':['amc','entertainment','meme','theatre'],
             'GME':['gme','gamestop','game','gaming','meme'],
             'NVDA':['nvda','nvidia','video','gpu'],
             'PYPL':['pypl','paypal','payment'],
             'INTC':['intc','intel','chip','processor'],
             'ABNB':['abnb','airbnb','travel','rent','holiday']}


    for word in words[ticker]:
        if word in headline.lower():
            return True
    return False


def get_crypto_news(ticker):
    """A function that retrieves the news articles headlines and urls for a given crypto currency using its ticker. The
       cryptonews API is used to get the described information. Only articles posted on the current day are considered.

       Params:
       ticker: str - The cryptocurrency ticker

       Returns:
       news: dictionary - A dictionary containing the news headlines and their urls
       """

    # cryptonews API
    endpoint = 'https://cryptonews-api.com/api/v1?tickers={}&items=50&token=lkiy82hxgpzxkie77hzz5mwjyoeemst9abdb31xk'.format(
        ticker)

    # Get the API response and check if the status code is OK(200)
    response = requests.get(endpoint)
    if response.status_code==200:
        pass
    else:
        return False

    news = {}

    # The response is converted to json format. The payload is contained in key data
    for item in response.json()['data']:
        # Check if the article's date is relevant
        str_date = item['date'][5:16]
        date = datetime.strptime(str_date, "%d %b %Y")
        if date.month==current_date.month and date.day==current_date.day:
            # Add the headline - url pair to news
            news[item['title']] = item['news_url']

    return news
