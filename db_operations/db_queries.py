import datetime

from psycopg2 import Error
from db_operations import db_updates
import numpy as np
import pandas as pd
from datetime import timedelta

def get_count_stats(ticker,date):
    """A function that queries the database and retrieves the negative/neutral/positive proportion of
       articles for a given stock/cryptocurrency on a given day present in the database.

       Params:
       ticker: str - The stock/cryptocurrency ticker.
       date: datetime object - The date for which results are to be retrieved.

       Returns:
       sentiment_counts: list - A list of the negative/neutral/positive number of articles in the db.

       """

    # format the date that will be used for the query.
    current_date=str(date.year)+"-"+str(date.month)+"-"+str(date.day)
    limit_date = date + timedelta(days=1)
    limit_date = str(limit_date.year) + "-" + str(limit_date.month) + "-" + str(limit_date.day)

    sentiment_classes=['negative','neutral', 'positive']
    sentiment_counts=[]

    # Query the database for the number of articles for each sentiment class
    for sent in sentiment_classes:
        query = "SELECT COUNT(overall_sent) FROM (SELECT ticker,overall_sent FROM entryinfo NATURAL JOIN " \
                   "sentiment WHERE overall_sent={} AND ticker={} AND date_time BETWEEN {} AND {}) AS a1".format("'"+sent+"'","'"+ticker+"'",
                                                                                                "'"+current_date+"'","'"+
                                                                                                                    limit_date+"'")
        try:
            connection, cursor = db_updates.connect_to_db()
            cursor.execute(query)
            response=cursor.fetchone()[0]
            sentiment_counts.append(response)
        except (Exception,Error) as error:
            print("Something went wrong when fetching article stats..")
            print(error)
        finally:
            cursor.close()
            connection.close()

    return sentiment_counts

def get_sentiment_stats(ticker,date):
    """A function that retrieves the sentiment statistics for a given stock/cryptocurrency. Two types of statistics are calculated:
       Firstly, in order to generate a sense for the scalar negativity of the negative articles, the negative probabilities of
       all articles evaluated as overall negative(based on the max probability of the three classes) are pooled. The same is repeated
       for the positive articles. Having generated the scalar representations of the 'expressed negativity' in negative articles
       and 'expressed positivity' of positive articles, a final scalar representation of the overall sentiment towards the stock/cryptocurrency
       is constructed. Weights are assigned to each scalar representation based on the number of articles in the given class.
       The following formula is applied to deduce the scalar sentiment: (-neg_weight*scalar_negativity)+(pos_weight*scalar_positivity)*100,
       where neg_weight =num_negative_articles/total_articles and pos_weight=num_positive_articles/total_articles. Essentially,
       the scalar goes from -100(very negative) to 100(very positive) where 0 is considered neutral.

       Params:
       ticker: str - The stock/cryptocurrency ticker.
       date: datetime object - The date for which results are to be retrieved.

       Returns:
       pos_neg_scalars: list - The scalar(expressed) positivity and negativity in positive and negative articles respectively(towards a given stock, on a given day).
       sentiment_scalar: float - The overall scalar sentiment towards a given stock/cryptocurrency on a given day.
       """

    current_date=str(date.year)+"-"+str(date.month)+"-"+str(date.day)
    limit_date = date + timedelta(days=1)
    limit_date = str(limit_date.year) + "-" + str(limit_date.month) + "-" + str(limit_date.day)

    sentiment_classes=['negative','positive']
    num_negative_articles=0
    num_positive_articles=0
    pos_neg_scalars=[]

    # Get the articles for each sentiment class and calculate the respective scalar.
    for sent in sentiment_classes:
        # Query the database for the sentiment probabilities of each article for the given ticker on the given date.
        query = "SELECT a1.sentiment_prob FROM (SELECT overall_sent,sentiment_prob FROM entryinfo NATURAL JOIN " \
            "sentiment WHERE overall_sent={} AND ticker={} AND date_time BETWEEN {} AND {}) AS a1".format("'"+sent+"'","'"+ticker+"'",
                                                                                         "'"+current_date+"'","'"+limit_date+"'")
        try:
            connection,cursor = db_updates.connect_to_db()
            cursor.execute(query)
            response=cursor.fetchall()

            # Check whether there is any data in the response.
            if len(response) >0:

                # Convert to numpy ndarray for further processing.
                arr=np.array(response)
                if sent=='negative':
                    num_negative_articles=len(response)

                    # Mean pool along the column axis and retrieve the pooled negative probability of negative articles.
                    score=np.mean(arr,axis=0)[0][0]

                else:
                    num_positive_articles=len(response)

                    # Mean pool along the column axis and retrieve the pooled positive probability of positive articles.
                    score=np.mean(arr,axis=0)[0][2]

                # Append the list holding both scalars.
                pos_neg_scalars.append(score)
            # Append 0 for the given scalar if there were no articles in the response.
            else:
                pos_neg_scalars.append(0)
        except (Exception,Error) as error:
            print("Something went wrong")
            print(error)
        finally:
            cursor.close()
            connection.close()

    # Calculate the overall sentiment scalar.

    # If there were no articles for both classes the sentiment scalar is zero.
    if sum(pos_neg_scalars)==0:
        sentiment_scalar=0

    else:
        # Calculate the weights and the overall sentiment scalar based on the formula in the function description.
        neg_weight= -1*(num_negative_articles/(num_negative_articles+num_positive_articles))
        pos_weight= num_positive_articles/(num_negative_articles+num_positive_articles)
        sentiment_scalar = ((neg_weight*(pos_neg_scalars[0])) + (pos_weight*pos_neg_scalars[1]))*100
        sentiment_scalar=float("%.2f" % sentiment_scalar)

        if sentiment_scalar%1==0:
            sentiment_scalar=int(sentiment_scalar)
    return pos_neg_scalars, sentiment_scalar

def _get_frequent_polarity_words(ticker, date, n):
    """A function that retrieves the n most occurring positive and negative words in the articles for a given stock/cryptocurrency
       based on the sentiment lexicon used. The functions returns three separate lists: the n most occurring positive,
       n most occurring negative, and a mixed list of the n most occurring positive and negative words. For context on why the third list
       is necessary: e.g [good,beautiful,tremendous,terrible,bad] - if the list was ordered ascendingly by frequency of occurrence,
       terrible would be the 3rd most occurring positive or negative word but the most occurring negative word.

       Params:
       ticker: str - The stock/cryptocurrency ticker.
       date: datetime object - The date for which results are to be retrieved.
       n: int - The number of most occurring words to be retrieved.

       Returns:
       n_most_posneg:list - A list of length n*2 of dictionaries each containing the word,sentiment,article headline and url for a given word.
                              The list follows a descending order based on frequency of occurrence.

       n_most_positive: list - A list of length n of dictionaries each containing the word,sentiment,article headline and url for a given positive word.
                              The list follows a descending order based on frequency of occurrence.

       n_most_negative: list - A list of length n of dictionaries each containing the word,sentiment,article headline and url for a given negative word.
                              The list follows a descending order based on frequency of occurrence.
       """

    # Get the dataframe containing all words from the articles for the given ticker that are present in the sentiment lexicon.
    df=_get_lexicon_df(ticker,date)


    sentiment_classes=['positive','negative']

    n_most_posneg=[]
    n_most_negative=[]
    n_most_positive=[]

    # Controlling for cases where there are no articles for a given ticker and the dataframe is empty.
    if df.size==0:
        return [],[],[]

    # For each word in range n*2 in the dataframe ordered in descending order based on frequency of occurrence append the mixed list.
    for word in df.word.value_counts().head(n*2).index:
        n_most_posneg.append({'word':word,'sentiment':df.query('@word in word').sentiment.all(),'headline':df.query('@word in word').headline.all()
                                        ,'url':df.query('@word in word').url.all()})

    # For each sentiment class construct a list that holds the word for a given class in descending order based on frequency of occurrence.
    for sent_class in sentiment_classes:
        sent_words=df[df['sentiment']==sent_class].word.value_counts().index

        # Append the lists of n_most_positive/negative words with the relevant data for each word.
        for word in sent_words:
            if sent_class=='positive':
                n_most_positive.append({'word':word,'sentiment':"positive",'headline':df.query('@word in word').headline.all()
                                        ,'url':df.query('@word in word').url.all()})
            else:
                n_most_negative.append({'word': word, 'sentiment': "negative", 'headline': df.query('@word in word').headline.all()
                                           , 'url': df.query('@word in word').url.all()})

    return n_most_positive[:n],n_most_negative[:n],n_most_posneg[:n*2]

def _get_lexicon_df(ticker,date):
    """A function that builds a dataframe of the polarity words occurring in the news articles and their corresponding sentiment.
       The sentiment lexicon was build based on Loughran & McDonald (2011)and Hu & Liu (2004).

       Params:
       ticker: str - The ticker for the given stock/cryptocurrency.
       date: datetime object - The date for which results are to be retrieved.

       Returns:
       df: pandas.DataFrame - A dataframe containing all polarity words that were present in the articles for the given
                              stock/cryptocurrency on the given day and their sentiment.
       """


    current_date=str(date.year)+"-"+str(date.month)+"-"+str(date.day)
    limit_date = date + timedelta(days=1)
    limit_date = str(limit_date.year) + "-" + str(limit_date.month) + "-" + str(limit_date.day)

    df=pd.DataFrame()

    # Query retrieving the lists of words and their corresponding sentiment, the headline of the article where they were present and its url.
    query = "SELECT words,sentiment_class,headline,url FROM polaritywords NATURAL JOIN entryinfo WHERE ticker={} AND date_time BETWEEN {} AND {}".format(
        "'" + ticker + "'", "'" + current_date+ "'","'"+limit_date+"'"
    )
    try:
        connection, cursor = db_updates.connect_to_db()
        cursor.execute(query)
        response = cursor.fetchall()
        # Check whether there is any data in the response
        if len(response) > 0:
            # For each item in the response lists append the dataframe with the corresponding information.
            for item in response:
                df=df.append(pd.DataFrame({'word':item[0],'sentiment':item[1],'headline':item[2],'url':item[3]}),ignore_index=True)
    except (Exception,Error) as error:
        print(error)
    finally:
        cursor.close()
        connection.close()

    return df



def get_keyphrases(ticker,date):
    """A function that retrieves the key phrases and data about the article they were derived from for a given stock/cryptocurrency on a given day.
       After retrieving all data, the key phrases are tagged for sentiment based on their assumed negativity or positivity.The process is carried out in the following manner:
       Firstly, based on the sentiment lexicon used, all polarity words from all articles for the given stock/cryptocurrency on the given date are extracted.
       Subsequently, the key phrases contain words also present in the sentiment lexicon are kept and tagged based on sentiment of the polarity words present in them.
       In addition to generating a sentiment tag for the phrases, applying the above method also ensures that there is less noise in the key phrases kept.

       Params:
       ticker: str - The ticker for the given stock/cryptocurrency.
       date: datetime object - The date for which results are to be retrieved.

       Returns:
       keyphrases_data: list - A list of dictionaries each containing a key phrase, the headline of the article it was derived from,
                               the url of the article, and a sentiment tag.


       """
    current_date=str(date.year)+"-"+str(date.month)+"-"+str(date.day)
    limit_date = date + timedelta(days=1)
    limit_date = str(limit_date.year) + "-" + str(limit_date.month) + "-" + str(limit_date.day)

    df=pd.DataFrame()
    # Query retrieving all keyphrases for a given stock/cryptocurrency on a given date.
    query = "SELECT phrases,headline,url FROM keyphrases NATURAL JOIN entryinfo WHERE ticker={} AND date_time BETWEEN {} AND {}".format(
        "'" + ticker + "'", "'" + current_date + "'","'"+limit_date+"'"
    )

    try:
        connection, cursor = db_updates.connect_to_db()
        cursor.execute(query)
        response = cursor.fetchall()
        # Check if the response contains any data.
        if len(response)==0:
            return [],[],[]
        else:
            # Generate a dataframe containing keyphrase information retrieved from the response.
            for item in response:
                df = df.append(pd.DataFrame({'phrase': item[0], 'headline': item[1], 'url': item[2]}),
                                 ignore_index=True)
    except (Exception, Error) as error:
        print(error)

    finally:
        cursor.close()
        connection.close()


    # Get the dataframe containing all words from the articles for the given ticker that were present in the sentiment lexicon.
    lexicon_df=_get_lexicon_df(ticker,date)


    # Conver the dataframe to a list of dictionaries to ease the insertion of an extra column for sentiment(it will be inserted as a key in each dict)
    df=df.to_dict(orient='records')


    for item in df:
        # For each phrase in the response iterate through all words in the dataframe.
        for word in set(lexicon_df['word'].tolist()):
            # If the phrase contains a sentiment word from the dataframe, retrieve the word's polarity update the dictionary.
            if word in item['phrase']:
                if lexicon_df.query("@word in word").sentiment.all()=='positive':
                    item['sentiment']='positive'
                else:
                    item['sentiment']='negative'

    # Convert the df back to a dataframe to drop all phrases that did not contain polarity words and then convert back to a list of dictionaries.
    keyphrases_data=pd.DataFrame(df).dropna().to_dict(orient='records')

    return keyphrases_data

def get_ticker_info(date):
    """A function that retrieves all information from table tickerinfo for all tickers for which data is collected. The information includes
    the ticker symbol, the full name of the stock/cryptocurrency, the number of articles for it on the given day and a url for its logo image.

    Params:
    date: datetime object - The date for which results are to be retrieved.

    Returns:
    ticker_info: dict - A dictionary of key-value pairs - ticker : dictionary containing keys: id, image_url, name, num_articles and ticker.
    """
    current_date = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
    limit_date = date + timedelta(days=1)
    limit_date =str(limit_date.year) + "-" + str(limit_date.month) + "-" + str(limit_date.day)

    query='SELECT id,tickerinfo.ticker,name,image_url,COUNT(entryinfo.ticker) FROM tickerinfo LEFT JOIN entryinfo ' \
          'ON entryinfo.ticker=tickerinfo.ticker AND date_time BETWEEN {} and {} GROUP BY tickerinfo.ticker'.format(
        "'"+current_date+"'","'"+limit_date+"'")

    try:
        connection,cursor= db_updates.connect_to_db()
        cursor.execute(query)
        response=cursor.fetchall()

    except (Exception,Error) as error:
        print(error)
    finally:
        cursor.close()
        connection.close()

    ticker_info={}
    for item in response:
        if item[1] in db_updates.TICKER_CLASSES['stock_tickers']:
            type='stock'
        else:
            type='crypto'
        ticker_info[item[1]] = {'id': item[0], 'image_url': item[3], 'name': item[2], 'num_articles': item[4], 'ticker': item[1],'type':type}

    return ticker_info

def get_headlines(ticker,date):
    """A function that retrieves the article headlines, their urls and overall sentiment for a given stock/cryptocurrency on the current day.
       Only the positive and negative articles are considered unless there are less than 5 of them, in which case neutral articles are retrieved too.
       Reason being, that sentiment expressing articles are the ones that ought to be considered relevant for any price swings. Additionally, they are the ones
       used in the calculation of the sentiment score. However, when they lack, the user will still be able to get context about the stock/cryptocurrency of interest.

       Params:
       ticker: str - The ticker symbol for the given stock/cryptocurrency.
       date: datetime object - The date for which results are to be retrieved.

       Returns:
       headlines: list - A list of dictionaries each containing the headline, url and sentiment for a given article.
    """
    current_date = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
    limit_date = date + timedelta(days=1)
    limit_date = str(limit_date.year) + "-" + str(limit_date.month) + "-" + str(limit_date.day)


    query = 'SELECT headline, url,overall_sent FROM entryinfo NATURAL JOIN sentiment' \
            ' WHERE ticker={} AND date_time BETWEEN {} AND {} AND overall_sent!={}'.format("'" + ticker + "'","'"+current_date+"'",
                                                                      "'"+limit_date+"'","'"+'neutral'+"'")

    # The query is executed in cases there are less than 5 positive or negative articles for the given ticker on the given day.
    neutral_query='SELECT headline, url,overall_sent FROM entryinfo NATURAL JOIN sentiment' \
            ' WHERE ticker={} AND date_time BETWEEN {} AND {}'.format("'" + ticker + "'","'"+current_date+"'",
                                                                      "'"+limit_date+"'")

    try:
        connection, cursor = db_updates.connect_to_db()
        cursor.execute(query)
        response = cursor.fetchall()
        # Execute the query retrieving neutral articles if there are less than 5 positive and negative ones.
        if len(response)<5:
            cursor.execute(neutral_query)
            response=cursor.fetchall()
    except (Exception, Error) as error:
        print(error)
    finally:
        cursor.close()
        connection.close()

    articles=[]
    for item in response:
        articles.append({'headline':item[0],'url':item[1],'sentiment':item[2]})

    return articles
