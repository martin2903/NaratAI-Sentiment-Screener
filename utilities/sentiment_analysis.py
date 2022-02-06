import numpy as np
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from scipy.special import softmax
from utilities import key_phrases
import os

#BERT is limited to a 512 tokens input. A balance between being able to tokenize longer sequences and computational cost was struck at 300.
MAX_TOKENS_LENGTH=300

# The below will allow the script to be ran from different working directories
dir = os.path.dirname(__file__)
path=os.path.join(dir, 'BertModel')

model = BertForSequenceClassification.from_pretrained(path)
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-cased')



def _split_input(text):
    """A function that splits the document(news article) into topical paragraphs. For details, check
       keywords._get_paragraphs

       Params:
       text: str - the document(news article) to be split into topical paragraphs of length MAX_LENGTH-NUM_SPECIAL_TOKENS

       Returns:
       paragraphs: list - the document split into topical paragraphs
       """
    paragraphs = key_phrases._get_paragraphs(text)

    return paragraphs

def get_sentiment(text):
    """"A function that retrieves the sentiment of a document(news article). The class probabilities for each class of each paragraph
        are obtained and averaged to arrive at an overall probability for each class of the entire document(see _get_class_probabilities)

        Params:
        text: str - the text document(news article)

        Returns:
        overall_prediction: str - The class that has the overall highest probability for the article(on the ternary scale of negative/neutral/positive)
        class_probabilities: list -A list of the probabilities for each class obtained by _get_class_probabilities
        """

    classes=['negative','neutral','positive']

    #Split the document in topical paragraphs
    paragraphs = _split_input(text)

    #Get all the encodings to be fed to the model
    encodings =bert_tokenizer.batch_encode_plus(paragraphs,add_special_tokens=True,padding='max_length',max_length=300,
                                                return_attention_mask=True,return_tensors='pt')

    #Get the model output. torch.no_grad() is used as there is not need to calculcate gradients which is otherwise automatically done by pytorch
    with torch.no_grad():
        output= model(encodings['input_ids'],encodings['attention_mask'])

    #Get the probabilities for each class of the entire document
    class_probabilities = _get_class_probabilities(output)

    #Get the overall prediction for the document based on the index of the maximum probability obtained from np.argmax
    overall_prediction = classes[np.argmax(class_probabilities)]

    return overall_prediction,class_probabilities


def _get_class_probabilities(model_output):
    """A function that get the probabilities for each class of a document by averaging the probabilities for each paragraphs.
       First, the paragraph probabilities are obtained using a softmax function before averaging them to arrive at the final probabilities.
       Due to observations about the model's performance and the semantic structure of news articles, neutral probabilities are reduced
       by 50% to avoid misclassifications.

       Params:
       model_output: transformers.modeling_outputs.SequenceClassifierOutput - the output of the BERT model

       Returns:
       class_probabilities: list - a list of len=3 where indexes 0,1,2 correspond to classes negative, neutral, and positive respectively

       """

    #Get the model output logits(output of the fully connected linear layer)
    output_logits = model_output[0]

    #Get the probabilities for each class of each paragraphs
    paragraph_probabilities = softmax(output_logits.numpy(),axis=1)
    paragraph_probabilities[:, 1] = paragraph_probabilities[:, 1] / 2

    #Get the average probability for each class of the entire document by summing each paragraph probability and dividing by the number of paragraphs
    num_paragraphs = paragraph_probabilities.shape[0]
    class_probabilities = np.sum(paragraph_probabilities,axis=0)/num_paragraphs

    return class_probabilities.tolist()

