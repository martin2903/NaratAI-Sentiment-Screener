import datetime
import flask
from flask import jsonify, request
from db_operations import db_queries
from datetime import datetime, timedelta

app = flask.Flask(__name__)

app.config['DEBUG'] = True


@app.route('/gettickers', methods=['GET'])
def get_tickers():
    """ A function that serves the /gettickers endpoint. The function retrieves the ticker symbol, name, number of
        articles and image url for each stock/cryptocurrency in the database.

        Params:
        none

        Returns:
        response: JSON response object containing the above described data.
    """

    # Get the ticker information for the current day.
    response = db_queries.get_ticker_info(datetime.now())

    # Convert to json and add headers required by browsers.
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/getkeyphrases', methods=['GET'])
def get_phrases():
    """ A function that serves the /getkeyphrases endpoint. It retrieves all keyphrases for a given ticker present
        in the current day's news articles(see db_queries.get_keyphrases for details).

        URL Params:
        ticker: the ticker symbol of the given stock/cryptocurrency

        Returns:
        response: JSON response object containing the above described data.
        """
    # Fetch the ticker parameter value received in the GET request.
    t = request.args.get('ticker')

    keyphrases = db_queries.get_keyphrases(t, datetime.now())
    # Convert to JSON format and add the headers required by browsers.
    response = jsonify(keyphrases)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/getstats', methods=['GET'])
def get_stats():
    """ A function that serves the /getstats endpoint. It retrieves the number of negative,neutral, and positive
        articles for a given ticker on the current day.

        URL Params:
        ticker: The ticker symbol of the given stock/cryptocurrency

        Returns:
        response: JSON response object containing the above described data.
       """

    # Fetch the ticker parameter value received in the GET request.
    t = request.args.get('ticker')

    article_counts = db_queries.get_count_stats(t, datetime.now())
    # Convert a dictionary of the stats to JSON format and add the headers required by browsers.
    response = jsonify({'negative': article_counts[0], 'neutral': article_counts[1], 'positive': article_counts[2]})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/getsentimentscore', methods=['GET'])
def get_sentiment_score():
    """A function that serves the /getsentimentscore endpoint. The function retrieves the sentiment score
       for one or multiple tickers on the current day.

       URL Params:
       ticker: The ticker symbol/s for the given stock(s)/cryptocurrency(ies)

       Returns:
       response: JSON response object containing the above described data.
     """

    # Fetch the ticker parameter value received in the GET request and split if there are multiple values.
    args = request.args.get('ticker')
    tickers = args.split(',')
    response = {}

    # For each ticker passed in the GET request get the sentiment score.
    for ticker in tickers:
        response[ticker] = db_queries.get_sentiment_stats(ticker, datetime.now())[1]

    # Convert to JSON format and add the headers required by browsers.
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/gethistoricalscore', methods=['GET'])
def get_historical_score():
    """A function that serves the /gethistoricalscore endpoint. The function retrieves the sentiment scores for a given ticker
       for a given time period.

       URL Params:
       ticker: The ticker symbol for the given stock/cryptocurrency.
       period: The time period for which sentiment scores are to be retrieved.

       Returns:
       response: JSON response object containing the above described data.
     """

    # Fetch the ticker and period parameter values received in the GET request.
    ticker = request.args.get('ticker')
    period = int(request.args.get('period'))

    results = []
    # For each time unit in the period retrieve the sentiment score and append the results array.
    for time_unit in range(period):
        date = datetime.now() - timedelta(days=time_unit)
        results.append(db_queries.get_sentiment_stats(ticker, date)[1])
    # The array is reversed as it eases operations on the frontend.
    results = results[::-1]

    # Convert to JSON format and add the headers required by browsers.
    response = jsonify(results)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/getheadlines', methods=['GET'])
def get_headlines():
    """ A function that serves the /getheadlines endpoint. It retrieves the headlines, urls and sentiment of articles
        for a given ticker on a given day.

        URL Params:
        ticker: The ticker symbol for the given stock/cryptocurrency.

        Returns:
        response: JSON response object containing the above described data.
        """

    # Fetch the ticker parameter value received in the GET request and split if there are multiple values.
    ticker = request.args.get('ticker')
    headlines = db_queries.get_headlines(ticker, datetime.now())

    # Convert to JSON format and add the headers required by browsers.
    response = jsonify(headlines)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/getpolaritywords', methods=['GET'])
def get_polaritywords():
    """ A function that serves the /getpolaritywords endpoint. It retrieves the 10 most occurring positive, 10 most occurring negative
        and 10 most occurring positive and negative words(see db_queries._get_frequent_polarity_words for context on the difference
        between the lists containing only negative or positive words and the list containing both).

        URL Params:
        ticker: The ticker symbol for the given stock/cryptocurrency.

        Returns:
        response: JSON response object containing the above described data.
        """
    # Fetch the ticker parameter value received in the GET request and split if there are multiple values.
    ticker = request.args.get('ticker')
    # get the most occurring positive, negative and positive and negative words.
    pos_words, neg_words, all_words = db_queries._get_frequent_polarity_words(ticker, datetime.now(), 10)

    # Convert to JSON format and add the headers required by browsers.
    response = jsonify({'positive': pos_words, 'negative': neg_words, 'all': all_words})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run(debug=True)
