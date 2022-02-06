import pandas as pd
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import VaderConstants as vader
import os
import requests
from newspaper import fulltext

dir = os.path.dirname(__file__)
path=os.path.join(dir, '../project_datasets/sentiment_lexicon.csv')
lexicon = pd.read_csv(path)


def _neg_marking(text):
    """A function that receives a document(news article) as a parameter and applies negation marking. Words preceded by a negation term
       are marked with a _NEG tag. Negation terms are extracted from the Vader library. Based on literature the following rules are applied:
       - A word is tagged with a _NEG tag if it is preceded within 3 words by a negation term and no punctuation separates them.
       - Following a comma or a full stop, negation tagging is terminated.
       Before marking, the text is tokenized using TweetTokenizer as after attempting numerous others tokenizers, TweetTokenizer
       seemed to perform best at detecting punctuation and generating sensible tokens.

       Params:
       text: text - The the document(news article) to be marked.

       Returns:
       neg_marked_tokens: list - A list of all tokens tokenized by TweetTokenizer marked for negation.

       """

    tokens = TweetTokenizer().tokenize(text)

    #A boolean tag that is set to True whenever negation marking should be applied based on the rules described
    punct = False

    #A variable tracking the word count as negation is applied only on words preceded within 3 words by a negation term
    count=0


    for index, word in enumerate(tokens):
        # if a negation term is encountered set the boolean flag to True
        if word in vader.NEGATE and not punct and count<3:
            punct=True
            continue
        # Tag all words that are not negation terms themselves and increment count
        if punct and word not in vader.NEGATE:
            count+=1
            tokens[index]=tokens[index]+"_NEG"
        # When reaching the described punctuation or exceeding the window of 3 words set the flag back to False and reset the count
        if word ==',' or word =='.' or count==3:
            punct=False
            count=0

    return tokens


def get_sentiment_scores(tokens,lexicon_df):
    """A function that looks up which words from the words processed by _neg_marking are present in the
       lexicon dataframe and retrieves their sentiment tag. Based on literature, Loughran & McDonald (2011)
       and Hu & Liu (2004) were the sentiment lexicons selected.

       Params:
       tokens: list - The list of tokens marked for negation by _neg_marking.
       lexicon_df: pandas.Dataframe - the dataframe containing the two lexicons (details on generating the csv file are
                                                                                can be found in the 'Sentiment Lexicon Generation' notebook).

       Returns:
       words: list - The words that were present in the lexicon dataframe. Words tagged for negation have the _NEG tag
                     removed and replaced by 'not' before the word. E.g, token 'great_NEG' becomes 'not great'.
       sentiment: list - The corresponding sentiment for each word in words.

       """

    # Generate a list of all words from tokens that are present in the lexicon dataframe
    words = [word.lower() for word in tokens if word.split("_NEG")[0].lower() in list(lexicon_df.word)]
    sentiment = []

    # Get the sentiment for each word in words
    for index, word in enumerate(words):
        # If the word has a _NEG tag, invert its sentiment
        if '_neg' in word:
            if lexicon_df.query('@word.split("_neg")[0] in word').sentiment.all() == 'positive':
                sentiment.append('negative')
            else:
                sentiment.append('positive')
        else:
            sentiment.append(lexicon_df.query('@word in word').sentiment.values[0])

    # Replace the _NEG tags in words with 'not'
    words = ['not ' + word.split("_neg")[0] if "_neg" in word else word for word in words]


    return words,sentiment

def get_polarity_words(text):
    """A function that retrieves all polarity words with negation being considered from a given news article"""
    return get_sentiment_scores(_neg_marking(text),lexicon)

if __name__ =='__main__':
    text = requests.get('https://finance.yahoo.com/news/5-tesla-surmounts-supply-chain-153950361.html').text
    parsed = fulltext(text)
    tokens = _neg_marking(parsed)
    words = [word.lower() for word in tokens if word.split("_NEG")[0].lower() in list(lexicon.word)]
    print(words)
    sentiment=[]
    print(lexicon.query('@words[1] in word').sentiment.values[0])