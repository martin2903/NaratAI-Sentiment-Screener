# NaratAI Sentiment Screener

## Project Goal

NaratAI was inspired by Robert Schiller’s ‘Narrative Economics’ (Schiller , 2019). The name hints at what the application seeks to do – communicate the prevailing narrative for any given asset investors might be interested in.
The application was developed to address the problem of access to condensed, high- quality information on news sentiment and the driving factors behind it, both being one of the most imperative factors when considering a given investment. The software enables users to not only get a rapid understanding about the spectrum of negativity or positivity expressed for an asset of their choice but also explore the context of what is driving that polarity. The intended target audience consists of retail investors of which there has been a large recent influx. That group rarely has access to sophisticated data analytics like institutional investors do and is also characterized by mainly using online media outlets as a guide for investment decisions. The application addresses the group’s needs by providing high-quality dense information using the same technologies that market actors with significantly more dedicated resources also use. Additionally, considering the fact that a constraining resource for many retail investors is time, the software serves the purpose of saving users the need to collect and analyse that information themselves from the extremely large pool of sources available.

## Intersection of Science and Practicality

The software was developed by consulting the highest-quality contemporary literature on the topics of natural language understanding and linguistics. A novel approach to sentiment analysis and polarity words extraction previously not adopted by literature was employed. The evaluation of the machine learning model built shows that almost 80% of news articles' sentiment is correctly interpreted. 

## Overview
The core functionality of the application relies on a dataset of aggregated news articles. In order to acquire news articles for each of the supported stocks or cryptocurrencies, two separate news scrapers were built – one for stock news and another for crypto currency news. Following the acquisition of texts, each one is pre-processed before extracting its sentiment, key phrases and polarity words using a state-of-the-art NLU architecture and novel logic depicted in section 6 in ['NaratAIProject'](https://github.com/martin2903/NaratAI-Sentiment-Screener/blob/master/NaratAIProject.pdf). Next, the application database is updated with the described data for each news article scraped. Lastly, API endpoints serve data for consumption by the user interface. Refer to section 4.1 in ['NaratAIProject'](https://github.com/martin2903/NaratAI-Sentiment-Screener/blob/master/NaratAIProject.pdf) for a graphical representation of the process flow.

## Further Details

The reader can consult ['NaratAIProject'](https://github.com/martin2903/NaratAI-Sentiment-Screener/blob/master/NaratAIProject.pdf) for details on every step of the software development lifecycle. The consulted research and the methodology used for building the machine learning model responsible for the core functionality of the software is discussed in great detail.

## Folder Structure and File Depiction

* [**db_operations**](https://github.com/martin2903/NaratAI-Sentiment-Screener/tree/master/db_operations): Contains the scripts used for processing the scraped news articles and updating the database with the extracted data. Additional scripts for querying the database and applying further processing are also contained in that directory.
* [**utilities**:](https://github.com/martin2903/NaratAI-Sentiment-Screener/tree/master/utilities) Contains the scripts that enable the core functionality of the application. The reader can familiarize themselves with the methods used for analyzing articles' sentiment and extracting polarity words from them. The news scrapers built for acquiring articles' texts are also available in that directory.
* [**project_notebooks**](https://github.com/martin2903/NaratAI-Sentiment-Screener/tree/master/utilities): Contains all notebooks relating to the development of the machine learning model. The reader can explore how the data used was gathered, structured and analysed. Furthermore, the set-up for fine-tuning the BERT model is also depicted in great detail.
* [**external_datasets**](https://github.com/martin2903/NaratAI-Sentiment-Screener/tree/master/external_datasets): Contains all external datasets prior to structuring them for the purposes of this project.
* [**project_datasets**](https://github.com/martin2903/NaratAI-Sentiment-Screener/tree/master/project_datasets): Contains the processed external datasets that were used for fine-tuning the neural language model and for enabling the key phrase extraction functionality.
* [**front_end**](https://github.com/martin2903/NaratAI-Sentiment-Screener/tree/master/front_end): Contains the React application.
* [**tests**](https://github.com/martin2903/NaratAI-Sentiment-Screener/tree/master/tests): Contains unit tests used to ensure the robust functioning of the software.
* [**app**](https://github.com/martin2903/NaratAI-Sentiment-Screener/blob/master/app.py): The Flask API endpoints.
* [**update_database**](https://github.com/martin2903/NaratAI-Sentiment-Screener/blob/master/update_database.py): A script for updating the application database.
* [**NaratAIProject**](https://github.com/martin2903/NaratAI-Sentiment-Screener/blob/master/NaratAIProject.pdf): The document depicting the entire project. The reader is strongly encouraged to consult it for further details on the practical and scientific merit of the project.

## Running the application

* The application was deployed on a Heroku server for presentation purposes and is available at **http://naratai.herokuapp.com/**.
* Should the reader wish to rebuild the application using the source code, the exported model will need to be added. That could be made possible by either
recreating the fine-tuning process using the 'BERT Fine-tuning' notebook or by getting in touch with me.
* If the application is to be pointed at a local PostgreSQL database instance, the credentials described in [db_updates](https://github.com/martin2903/NaratAI-Sentiment-Screener/blob/master/db_operations/db_updates.py) will need to be configured.


