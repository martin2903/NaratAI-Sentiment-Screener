import requests
import traceback
from newspaper import fulltext
import psycopg2
from psycopg2 import Error
from datetime import datetime
from utilities import sentiment_analysis, polarity_words, key_phrases, news_scrapers


# The stock and crypto tickers that will be considered when updating the database
TICKER_CLASSES={'stock_tickers':['TSLA', 'GOOG', 'AMZN', 'HOOD', 'NFLX', 'AAPL','FB','AMC','GME','NVDA','PYPL','INTC','ABNB'],
             'crypto_tickers':['BTC','ETH','DOGE','XRP','ADA','LTC','BNB','LINK','SHIB']}

def connect_to_db():
    """A function that establishes the connection to the PostgreSQL database using the psycopg2 adapter.

       Params: None

       Returns:
       connection: psycopg2.extensions.connection - The connection to the database.
       cursor: psycopg2.extensions.cursor - A cursor allowing for python code to execute PostgreSQL commands.

       """

    # Parameters needed to establish the connection
    USER = 'martin2903'
    PASSWORD = 'rocesM12?!'
    HOST = 'naratai.ccfiils8uwgj.eu-west-2.rds.amazonaws.com'
    PORT = '5432'
    DATABASE = 'postgres'
    try:
        connection=psycopg2.connect(user=USER,password=PASSWORD,
                                      host=HOST,port=PORT,
                                      database=DATABASE)
        cursor = connection.cursor()
    except (Exception,Error) as error:
        print('Something went wrong....',error)

    return connection,cursor



def update_db(connection,cursor):
    """A function that updates the database by updating all columns in all four tables for each news article scraped from the web
       for all stocks and cryptocurrencies listed in TICKER_CLASSES.

       Params:
       connection: psycopg2.extensions.connection - The established connection to the database.
       cursor: psycopg2.extensions.cursor - A cursor allowing for python code to execute PostgreSQL commands.

       Returns:
       None: Void function that updates the database.

    """

    # Loop through both ticker classes in TICKER_CLASSES
    for key in TICKER_CLASSES.keys():
        # For each ticker in a given ticker class get the news
        for ticker in TICKER_CLASSES[key]:
            # Scrape from finviz using get_stock_news
            if key == 'stock_tickers':
                news= news_scrapers.get_stock_news(ticker)
            # Scrape using the crypto news API using get_crypto_news
            else:
                news= news_scrapers.get_crypto_news(ticker)

            # Check whether there returned news dictionary is not empty (no news available for the given day for the given stock/cryptocurrency)
            if len(news)>0:
                # Update the database with information retrieved from each news article
                for headline,url in news.items():
                    _insert_entry(connection,cursor,headline,ticker,url)







def _check_parsing(url):
    """A function that checks whether the text from an article can be correctly parsed. Some websites do not allow scraping
       response status codes other than 200 are returned (e.g 403), hence firstly that is checked for. In other cases, the response
       code is 200(OK) but the response states that the website does not allow for scraping hence the length of the response is checked.
       Lastly, the crypto news api sometimes includes urls that would throw exceptions when attempted to be parsed by newspaper.fulltext
       (e.g - YouTube urls). Such circumstances are also controlled for.

       Params:
       url: str - The news article url.

       Returns:
       boolean: True if the text from the given article url can be correctly parsed. False otherwise.
       """

    response= requests.get(url)

    # Check response status code
    if response.status_code!=200:
        return False

    # Control for urls that do not contain text to be parsed by newspaper.fulltext (e.g YouTube urls)
    try:
        article_body= fulltext(response.text)
    except:
        return False

    # Check whether the response is not a message stating that the website does not allow for scraping. 420 was deemed as an appropriate length after observing the average length of such responses.
    if len(article_body)>420:
        return True
    else:
        return False


def _insert_entry(connection,cursor,headline,ticker,url):
    """"A function that inserts all information retrieved from a single news article into the database.
        All columns in tables: entryinfo, sentiment, keyphrases, and polaritywords are updated with the
        values retrieved for the given news article.

        Params:
        connection: psycopg2.extensions.connection - The established connection to the database.
        cursor: psycopg2.extensions.cursor - A cursor allowing for python code to execute PostgreSQL commands.
        headline: str - The article headline.
        ticker: str - The stock/cryptocurrency ticker related to the article.
        url: str - The article url.

        Returns:
        boolean: True if the entry was correctly inserted. False otherwise.

    """

    # Check whether the article text can be correctly parsed from the url
    if not _check_parsing(url):
        return False

    # Check whether the attempted insertion is not a duplicate
    if _is_duplicate(cursor,url):
        return False

    # A timestamp will be inserted in db table entryinfo indicating the time of entry
    time = datetime.now()
    article_text =fulltext(requests.get(url).text)

    '''Update each table in the db with the relevant information. Four statements updating the different db tables are executed.Subsequently,
       all modifications are saved by committing. Despite _is_duplicate checking for duplicate entries, a second layer of protection is employed.
       Since duplicate articles must be avoided, a unique constraint was placed on column url in table entryinfo. 
       Whenever a duplicate value insertion is attempted, an exception is thrown that would render further insertions unsuccessfull. 
       Therefore, within the except block a commit statement is executed as otherwise all further
       attempts to execute a query will be denied by the db. The commit statement after an exception does not impact the state of the db
       in any way.
       '''
    try:
        print(headline)
        # Get a unique entry id for the current entry
        entry_id=_get_next_id(cursor)
        # Update table entryinfo
        entryinfo_statement='INSERT INTO entryinfo (entryid,ticker,headline,date_time,url) VALUES (%s,%s,%s,%s,%s);'
        cursor.execute(entryinfo_statement,(entry_id,ticker,headline,time,url))

        # Update table sentiment
        overall_sentiment, sentiment_probab = sentiment_analysis.get_sentiment(article_text)
        sentiment_statement = 'INSERT INTO sentiment (entryid,overall_sent,sentiment_prob) VALUES (%s,%s,%s);'
        cursor.execute(sentiment_statement,(entry_id,overall_sentiment,sentiment_probab))

        # Update table keyphrases
        phrases = key_phrases.get_keyphrases(article_text, (3, 3), 7)
        keyphrase_statement = 'INSERT INTO keyphrases (entryid, phrases) VALUES (%s,%s);'
        cursor.execute(keyphrase_statement,(entry_id,phrases))

        # Update table polarity_words
        words,sentiment= polarity_words.get_polarity_words(article_text)
        polarity_words_statement = 'INSERT INTO polaritywords (entryid,words,sentiment_class) VALUES (%s,%s,%s)'
        cursor.execute(polarity_words_statement,(entry_id,words,sentiment))
        print("ALL QUERIES EXECUTED")
        # Commit all updates made
        connection.commit()
        print('SUCCESS')
        print("################")
    # Handle any errors or constraint violations
    except (Exception, Error) as error:
        print('Something went wrong....', error)
        print(traceback.format_exc())
        if 'duplicate key value' in str(error):
            print("UNIQUE KEY CONSTRAINT VIOLATED!")
            connection.commit()
            return False


    return True

def _get_next_id(cursor):
    """A function that generates a new unique id for a db entry.
       The function fetches the last id used from the db and adds one to it to generate a new id

    Params:
    cursor: psycopg2.extensions.cursor - A cursor allowing for python code to execute PostgreSQL commands

    Returns:
    new_id: int - New id generated

    """

    new_id=-1
    try:
        query = "SELECT MAX(entryid) FROM entryinfo"
        cursor.execute(query)
        last_id=cursor.fetchone()[0]
        new_id=last_id+1
    except (Exception, Error) as error:
        print("Something went wrong....",error)

    return int(new_id)

def _is_duplicate(cursor,url):
    """A function that checks whether a duplicate insertion is being attempted. Since column url in table entryinfo has a unique constraint,
       the url of the entry currently being inserted is checked against the current entries in the db.

       Params:
       cursor: psycopg2.extensions.cursor - A cursor allowing for python code to execute PostgreSQL commands
       url: The article url

       Returns:
       boolean: True if the url is not present in the database. False otherwise

       """
    try:
        query="SELECT url FROM entryinfo WHERE url={}".format("'"+url+"'")
        cursor.execute(query)
        response=cursor.fetchone()

        # If no entry with the given url exists, the response returns None
        if response is None:
            return False
        # If an entry with such url exists, its value is returned
        else:
            print("DUPLICATE INSERTION ATTEMPTED...")
            return True
    except (Exception, Error) as error:
        print(error)
        return True





