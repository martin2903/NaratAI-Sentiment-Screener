import torch
import numpy as np
from transformers import BertForSequenceClassification, BertTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import TextTilingTokenizer
from nltk.tokenize import sent_tokenize
import os

# The below will allow the script to be ran from different working directories
dir = os.path.dirname(__file__)
path=os.path.join(dir, 'BertModel')
model = BertForSequenceClassification.from_pretrained(path)
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-cased')

#The special [CLS] and [SEP] token added whenever add_special_tokens=True
NUM_SPECIAL_TOKENS=2

#BERT is limited to a 512 tokens input. A balance between being able to tokenize longer sequences and computational cost was struck at 300.
MAX_TOKENS_LENGTH=300
ALLOWED_TOKENS_LENGTH= MAX_TOKENS_LENGTH - NUM_SPECIAL_TOKENS

def _get_candidates(text, n_gram_range):
    """A function that uses sklearn CountVectorizer to tokenize the text and remove stopwords in order to generate
       candidate keywords.

       Params:
       text: str - the news text to be tokenized
       n_gram_range: tuple - what n-grams range to consider when tokenizing. E.g (1,2) will generate both unigram and bigram candidates

       Returns:
       candidates: list - the list of candidate keyword/key phrases

     """

    # choose the range of length of the n-grams that the vectorizer will parse.
    n_gram_range = n_gram_range

    # whether or not to remove stopwords. Both were tested - removing stopwords seemed to generate better results.
    stop_words = "english"

    # generate the features dictionary
    count = CountVectorizer(ngram_range=n_gram_range,stop_words=stop_words).fit([text])

    # get the features in the dictionary
    candidates = count.get_feature_names_out()

    return candidates


def _get_candidate_reps(candidates):
    """A function to get the BERT representation of all words from the tokenized document. The model returns a tensor of shape (k,l,m) where k=number of examples(1), l=number of tokens, m=768(BERT embedding dimensions).
       In order to get the representation I am indexing into the last hidden state of the returned tensor and getting the 0th element of the second dimension - [example][token][embedding].
       Depending on the n-gram I choose I could have more than one token or also in some cases BERT represents one word with more than one tokens. Therefore, in such cases I am mean pooling the embeddings
       using along the column axis which generates the final embedding representation. Finally, I am reshaping the tensors and converting them to numpy to prepare them as input for get_cosine_similarity.

       Params:
       candidates: list - the tokens obtained from CountVectorizer

       Returns: word_reps - a list of the word embedding for each token reshaped so that they can be used as input to sklearn.metrics.pairwise.cosine_similarity
       """
    word_reps = []

    for word in candidates:
        encoding = bert_tokenizer.encode(word, add_special_tokens=False, return_tensors='pt')

        with torch.no_grad():
            rep = model(encoding, output_hidden_states=True)

        # if there are multiple tokens, their representation is pooled using mean pooling along the 0 axis
        if rep.hidden_states[-1][0].shape[0] > 1:
            embedding = torch.mean(rep.hidden_states[-1][0], axis=0).detach().numpy().reshape(1, -1)

        else:
            embedding = rep.hidden_states[-1][0][0].detach().numpy().reshape(1, -1)

        word_reps.append(embedding)

    return word_reps


def _get_doc_rep(text):
    """ A function that retrieves the BERT representation of the entire document. The special BERT [CLS] token
        is used as a representation of the entire sequence. The [CLS] token can be obtained by indexing into the final hidden state and getting
        the 0th element of the second dimension. In cases where the tokenized document exceeds MAX_TOKEN_LENGTH, the text tiling algorithm is applied
        to separate the document into topical paragraphs. Subsequently, the [CLS] tokens pertaining to each paragraph are pooled to arrive at
        a final representation for the document.

        Params:
        text: str - the document text(news article)

        Returns:
        doc_representation: numpy.ndarray of shape (1,768) - the [CLS] token embedding reshaped to be used as input to get_cosine_similarity

        """

    #Getting the document representation by pooling the [CLS] tokens of each paragraph if the tokenized document exceeds MAX_TOKENS_LENGTH
    if len(bert_tokenizer.tokenize(text))>ALLOWED_TOKENS_LENGTH:
        paragraphs=_get_paragraphs(text)
        doc_encoding=bert_tokenizer.batch_encode_plus(paragraphs,add_special_tokens=True,padding='max_length',max_length=MAX_TOKENS_LENGTH,return_attention_mask=True,return_tensors='pt')

        with torch.no_grad():
            model_output= model(doc_encoding['input_ids'],doc_encoding['attention_mask'],output_hidden_states=True)
        doc_representation= torch.mean(model_output.hidden_states[-1][0],axis=0).detach().numpy().reshape(1,-1)

    #If the tokenized document does not exceed MAX_TOKENS_LENGTH, there is no need for splitting, hence the [CLS] token of the sequence is considered as the document representation
    else:
        doc_encoding = bert_tokenizer.encode_plus(text, add_special_tokens=True, padding='max_length', max_length=MAX_TOKENS_LENGTH,
                                                  return_attention_mask=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model(doc_encoding['input_ids'], doc_encoding['attention_mask'], output_hidden_states=True)

        # Squeeze to remove the first dimension of size 1 and get the 0th element. I am converting to numpy as that will be needed later.
        doc_representation = model_output.hidden_states[-1].squeeze(0)[0].detach().numpy().reshape(1, -1)

    return doc_representation

def _get_paragraphs(text):
    '''A function that separates the document(news article) into topical paragraphs. Defensive programming is applied
       to control for two unlikely occurrences. First, in cases where a text is too short TextTilingTokenizer throws
       a ValueError as it cannot detect any topical paragraphs. Second, it could be possible, yet very unlikely, that even
       after a text is split into paragraphs, one or more of them are still longer than the maximum tokens allowed.
       In such cases the paragraph is split into sentences until no paragraph is longer than the maximum tokens allowed
       using _paragraph_to_sent which recursively calls itself until that condition is satisfied.

       Params:
       text: str - the document(news article) to be split into topical paragraphs of length MAX_LENGTH-NUM_SPECIAL_TOKENS

       Returns: list - the document split into topical paragraphs
       '''
    paragraphs=[]
    text_tiling_tokenizer=TextTilingTokenizer()
    try:
        paragraphs=text_tiling_tokenizer.tokenize(text)
    except:
        return _split_paragraphs([text])

    return _split_paragraphs(paragraphs)

def _split_paragraphs(paragraphs):
    """A function that recursively splits paragraphs that are longer than the maximum tokens allowed in two new paragraphs.

       Params:
       paragraphs: list - list of paragraphs obtained by TextTilingTokenizer

       Returns:
       list - a list of the paragraphs with the paragraphs longer than the maximum tokens allowed split into two new
              paragraphs.
       """
    tokenized_paragraphs = [bert_tokenizer.tokenize(paragraph) for paragraph in paragraphs]
    max_length_paragraph = max(len(paragraph) for paragraph in tokenized_paragraphs)

    if max_length_paragraph < ALLOWED_TOKENS_LENGTH:
        return paragraphs
    else:

        '''Split the paragraph exceeding MAX_TOKENS_LENGTH into sentences and then form two new paragraphs from them.
           In very rare cases an article might use certain punctuation(e.g listing many numbers using decimal points
           that will be detected as one sentence by sent_tokenizer and exceed MAX_TOKENS_LENGTH. Such situation will
           trigger infinite recursive calls, hence, when that happens the only detected sentence acquired by sent_tokenizer
           is split in two.'''
        sents = sent_tokenize(max(paragraphs, key=len))
        new_paragraphs = []

        if len(sents)==1:
            new_paragraphs.extend([sents[0][:len(sents[0])//2],sents[0][(len(sents[0])//2):]])
        else:
            mid = len(sents)//2
            new_paragraphs.extend([' '.join(sents[:mid]),' '.join(sents[mid:])])

        paragraphs.remove(max(paragraphs, key=len))
        paragraphs += new_paragraphs
    return _split_paragraphs(paragraphs)




def _get_cosine_similarity(doc_embedding, word_embeddings):
    """A function that creates an array of the cosine similarities of the representations of each token in the document and the document itself.
       The presumption is that word with a higher cosine similarity to the document likely represent something semantically significant for it.

       Params:

       doc_embedding -np.ndarray of shape (1,768) - the BERT representation of the entire document.

       word_embeddings - list of np.ndarray of shape (1,768) - the BERT representations for each word in the document

       Returns:
       similarities: nd.numpy.array - an array of all cosine similarities
       """
    similarities = []
    for rep in word_embeddings:
        '''squeezing to remove all dimensions of size 1 when appending the array. 
           (I will need that to get the indexes of the highest similarity values later.)'''
        similarities.append(cosine_similarity(doc_embedding, rep).squeeze())

    return np.array(similarities)


def get_keyphrases(text, n_gram_range, top_n_keyphrases):
    """"A function that retrieves all key phrases from a given text. Semantic similarity is determined based on the cosine
        similarity between the embeddings.

        Params:
        text: str - the document text(news article)
        n_gram_range: tuple - what n-grams to consider when tokenizing. E.g (1,2) will generate both unigram and bigram candidates
        top_n_keyphrases: int - how many of the most similar key phrases to return.

        Returns:
        keyphrases: list - the key phrases of the document. keyphrases[-1] will have the highest similarity to the document embedding.
    """

    # get the tokenized key word or key phrases candidates
    candidates = _get_candidates(text, n_gram_range)

    # get the BERT embedding representations for each candidate
    candidate_reps = _get_candidate_reps(candidates)

    # get the document representation
    doc_rep = _get_doc_rep(text)

    # get the cosine similarities of each candidate and the entire document
    cosine_similarities = _get_cosine_similarity(doc_rep, candidate_reps)

    # get an array of the indexes in cosine_similarities sorted in an ascending order based on their value
    sorted_cos_indexes = np.argsort(cosine_similarities)

    # get the key phrases from the document
    keyphrases = [candidates[i] for i in sorted_cos_indexes[-top_n_keyphrases:]]
    return keyphrases

