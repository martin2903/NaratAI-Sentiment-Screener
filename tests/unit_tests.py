import unittest
from psycopg2 import Error
import numpy as np
import requests
from newspaper import fulltext
from utilities import key_phrases,sentiment_analysis,polarity_words,news_scrapers
from db_operations import db_updates
from transformers import BertTokenizer


def clean_up(id):
    """A function that will be used to restore the database in its previous state after tests are ran."""
    # The example entry first needs to be deleted from all tables referencing entryid's primary key - entryinfo
    clean_up1 = "DELETE FROM sentiment WHERE entryid={}".format(id)
    clean_up2 = "DELETE FROM keyphrases WHERE entryid={}".format(id)
    clean_up3 = "DELETE FROM polaritywords WHERE entryid={}".format(id)
    clean_up4 = "DELETE FROM entryinfo WHERE entryid={}".format(id)
    queries = [clean_up1, clean_up2, clean_up3, clean_up4]
    try:
        connection, cursor = db_updates.connect_to_db()
        for query in queries:
            cursor.execute(query)
    except (Exception, Error) as error:
        print(error)
    finally:
        connection.commit()
        cursor.close()
        connection.close()

# A class containing all tests
class Tests(unittest.TestCase):
    # The test texts that will be used
    article_url = "https://finance.yahoo.com/news/tesla-shares-plummet-investigation-launched-152527551.html"
    article2_url = "https://www.forbes.com/sites/jonathanponciano/2021/09/03/solana-overtakes-dogecoin-ethereum-price-hits-4000/?sh=3087e31b3371"
    headers = {'User-Agent': 'Mozilla/5.0'}
    example_text = fulltext(requests.get(article_url,headers).text)
    long_text = fulltext(requests.get(article2_url,headers).text)
    texts=[example_text,long_text]
    bert_tokenizer = BertTokenizer.from_pretrained('bert-base-cased')



    def test_splitting(self):
        """System splits texts into paragraphs according to specification.
           No paragraph should exceed the maximum token length used for training the model, as that could
           harm its performance."""
        # Split the the article into paragraphs.
        paragraphs= sentiment_analysis._split_input(self.example_text)
        for paragraph in paragraphs:
            # Check whether each paragraph is less than 300 tokens after splitting.
            self.assertTrue(len(self.bert_tokenizer.tokenize(paragraph)) <= key_phrases.ALLOWED_TOKENS_LENGTH, "One or more paragraphs "
                                                                                                      "exceeded the maximum token length.")


    def test_probabilities(self):
        """System produces model outputs probabilities that are statistically meaningful and they follow the logic implemented.
           Namely, whether they sum to 1, having sclaed the neutral probability by 2 as it ought to be decreased by 50% according to specificaition.
           The logic of the actual performance of the model was tested during the model selection process.
           Refer to the 'Selecting Model' notebook."""

        # get the class probabilities after applying the logic reducing the neutral sentiment by 50%
        class_probabilities= sentiment_analysis.get_sentiment(self.example_text)[1]
        # scale back the neutral probability to its original value
        class_probabilities[1] =class_probabilities[1]*2
        # sum the probabilities rounding to 4 decimal places
        probabilities_sum = round(sum(class_probabilities),4)
        self.assertTrue(probabilities_sum==1,"Probabilities did not equal 1 after rescaling")

    def test_phrase_pooling(self):
        """System applies token embeddings mean pooling correctly.
           Each candidate key phrase must be represented by a tensor of shape (1,768) obtained
           after pooling all word embeddings in the trigram and all separate token embeddings for one word
           where one word was represented by more than 1 token."""

        candidates = key_phrases._get_candidates(self.example_text, (3, 3))
        reps = key_phrases._get_candidate_reps(candidates)
        for rep in reps:
            self.assertTrue(rep.shape==(1,768),"One or more tensors had an shape inconsistent with the expected one.")

    def test_correct_splitting(self):
        """System deals with splitting text when they have unorthodox punctuation - bullet points
           and are of long length(meaning a higher chance that recursive paragraph splitting will be required)"""

        paragraphs = key_phrases._get_paragraphs(self.long_text)
        concat_paragraphs=""
        for paragraph in paragraphs:
            self.assertTrue(len(self.bert_tokenizer.tokenize(paragraph)) <= key_phrases.ALLOWED_TOKENS_LENGTH, "One or more paragraphs "
                                                                                                      "exceeded the maximum token length.")

    def test_lost_text(self):
        """System does not lose the entirety of texts after splitting and no
           paragraph is lost. Two texts with different lengths and punctuational characteristics are checked."""
        # An array that will hold the concatenated paragraphs for both texts
        concat_texts=[]
        for text in self.texts:
            # Concatenate all paragraphs to arrive at the original text before splitting
            concat_paragraphs=""
            for paragraph in key_phrases._get_paragraphs(text):
                concat_paragraphs+=paragraph
            concat_texts.append(concat_paragraphs)
            # Assert that the length of the concatenated paragraphs is the same as the original texts.
        self.assertTrue(len(self.texts[0])-len(concat_texts[0]) in range(0,2) and
                        len(self.texts[1])-len(concat_texts[1]) in range(0,2))

    def test_negation_marking(self):
        """System applies the heuristic negation rule correctly."""
        example_sentence = "Analysts do not have a bullish prognosis for Tesla in the long-run, however, its short-term potential is still favorable"

        tokens = polarity_words._neg_marking(example_sentence)
        self.assertTrue(tokens[5]=='bullish_NEG' and tokens[20]=='favorable',"Negation marking was not correctly applied")

    def test_blocking_websites(self):
        """System restricts warning messages generated from websites that block scraping entering the database."""

        blocked_url = "https://www.investors.com/market-trend/stock-market-today/dow-jones-rallies-as-jobless-claims-fall-apple-stock-nears-new-high/?src=A00220"

        self.assertFalse(db_updates._check_parsing(blocked_url), "The warning message response was not detected")

    def test_duplicates(self):
        """System logic prevents the insertion of duplicate entries into the database."""
        try:
            query = "SELECT url FROM entryinfo LIMIT 10"
            connection,cursor= db_updates.connect_to_db()
            cursor.execute(query)
            duplicate_urls = cursor.fetchall()
            for url in duplicate_urls:
                self.assertTrue(db_updates._is_duplicate(cursor, url[0]), "Duplicate not detected")
        except:
            pass
        finally:
            cursor.close()
            connection.close()

    def test_duplicates_db(self):
        """System database prevents the insertion of duplicate entries and violation of primary key constraints."""

        try:
            query = "SELECT * FROM entryinfo LIMIT 1"
            connection, cursor = db_updates.connect_to_db()
            cursor.execute(query)
            response = cursor.fetchall()
            insert_query='INSERT INTO entryinfo (entryid,ticker,headline,date_time,url) VALUES (%s,%s,%s,%s,%s);'
            self.assertFalse(cursor.execute(insert_query,(response[0][0],response[0][1],response[0][2],response[0][3],response[0][4])))
        except:
            print("System did not detect violated UNIQUE and PRIMARY KEY constraints")
        finally:
            cursor.close()
            connection.close()

    def test_sentiment(self):
        """System database entries' overall sentiment corresponds to the highest class probability"""

        classes= ['negative','neutral','positive']
        try:
            connection, cursor= db_updates.connect_to_db()
            # Get all articles' overall sentiment and corresponding sentiment probability
            query= "SELECT overall_sent, sentiment_prob FROM sentiment LIMIT 20"
            cursor.execute(query)
            response=cursor.fetchall()
            for item in response:
                # Assert that the overall sentiment class is the class with corresponding maximum probability in the probabilities array
                self.assertTrue(classes.index(item[0])==np.argmax(np.array(item[1])))
        except Exception:
            print(Exception)
        finally:
            cursor.close()
            connection.close()

    def test_polaritywords(self):
        """System entires' polarity words have a corresponding sentiment"""

        try:
            query = "SELECT words, sentiment_class FROM polaritywords LIMIT 200"
            connection,cursor = db_updates.connect_to_db()
            cursor.execute(query)
            response=cursor.fetchall()
            for item in response:
                self.assertTrue(len(item[0])==len(item[1]))
        except Exception:
            print(Exception)
        finally:
            cursor.close()
            connection.close()


    def test_relevancy(self):
        """System prevents the insertion of articles with irrelevant context for the given asset"""

        true_headlines=['Elon Musk Hosted a Tesla All Hands Meeting. Heres What Happened.','Tesla Stock Holds Buy Point As CEO Elon Musk Finally Admits To Key Delays',
                           'U.S. probing fatal Tesla crash that killed pedestrian']
        false_headlines = ['Match Group Surges 11% Postmarket on Planned S&P 500 Inclusion',
                           'The Story of Uber']
        for headline in true_headlines:
            self.assertTrue(news_scrapers._check_headline_relevancy(headline, 'TSLA'), "A relevant headline was evaluated as irrelevant")
        for headline in false_headlines:
            self.assertFalse(news_scrapers._check_headline_relevancy(headline, 'TSLA'), "An irrelevant headline was not detected")

    def test_insertion_info(self):
        """System layers integrate well to generate correct entries in tables."""
        article_url = "https://www.cnbc.com/2021/09/03/bitcoin-rises-this-week-to-51000-highest-since-may.html"
        headline='Bitcoin rises this week to $51,000, highest since May'
        ticker="BTC"

        try:
            connection, cursor = db_updates.connect_to_db()
            # Get the previous highest id
            query="SELECT MAX(entryid) FROM entryinfo"
            cursor.execute(query)
            last_id=int(cursor.fetchone()[0])

            # Insert example entry
            db_updates._insert_entry(connection, cursor, headline, ticker, article_url)
            cursor.execute(query)
            # Get the entryid of the last inserted entry
            new_id = int(cursor.fetchone()[0])

            # Get all data for the last entry in table entryinfo
            data_query='select * from entryinfo NATURAL JOIN sentiment NATURAL JOIN keyphrases ' \
                       'NATURAL JOIN polaritywords where entryid in (select max(entryid) from entryinfo)'
            cursor.execute(data_query)
            response = cursor.fetchall()
            # Check whether data in table entryinfo is correctly inserted
            self.assertTrue(new_id==last_id+1 and response[0][1]=="BTC" and response[0][4]==article_url)
            # Check whether data in table sentiment is correctly inserted
            self.assertTrue(response[0][6]=='positive' and response[0][6].index(max(response[0][6]))==2)
            # Check whether keyphrases were inserted
            self.assertTrue(len(response[0][7])>0)
            # Check whether polarity words were inserted
            self.assertTrue(len(response[0][8])>0)

        except (Exception, Error) as error:
            print(error)
        finally:
            cursor.close()
            connection.close()
            clean_up(new_id)













