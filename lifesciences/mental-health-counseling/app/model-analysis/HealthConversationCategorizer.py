import opendatasets as od 
import pandas as pd 
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from collections import defaultdict
import heapq

from transformers import pipeline
from torch import device, mode
import textwrap
from typing import List, Dict
from curses.ascii import isalpha
import token



DATA_DIR = '../../data'

class HealthConversationCategorizer:

    def __init__(self, model_name:str, max_tokens:int = 512):
        #pre-trained model used for sentiment analysis
        self.model_name = model_name
        self.lemmatizer = WordNetLemmatizer()
        # max # of tokens supported by the given model
        self.batch_size = max_tokens
        # max # of sentences in a summarized text
        self.num_sentences = 3



    def _get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # Default to noun


    def _lemmitize(self, text):
        tokens = word_tokenize(text.lower())
        tagged_tokens = pos_tag(tokens)
        lemmatized = [
            self.lemmatizer.lemmatize(token, self.get_wordnet_pos(pos))
            for token, pos in tagged_tokens
            if token.isalpha()
        ]
        return ' '.join(lemmatized)


    def _summarize_text(text: str, num_sentences: int) -> str:
        sentences = sent_tokenize(text)
        stop_words = set(stopwords.words('english'))
        word_frequencies = defaultdict(int) # 

        # In each sentence within txt, remove stop words and numbers, get each word frequency
        for sentence in sentences:
            for word in sentence.lower().split():
                if word.isalpha() and word not in stop_words:
                    word_frequencies[word] += 1

        # scaling freqs to 1 (Min-Max scaling)
        maximum_frequency = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word] / maximum_frequency)
        
        # calc score for each sentence based on word freq
        sentence_scores = defaultdict(int)
        for sentence in sentences:
            for word in sentence.lower().split():
                if word.isalpha() and word in word_frequencies:
                    sentence_scores[sentence] += word_frequencies[word]
                    # print("sentence score: ", sentence_scores)

        summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        return ' '.join(summary_sentences)


    def _get_model_pipeline(self) :
        """_summary_

        Returns:
            _type_: _description_
        """
        # using auto tokenizer - str to tokens (numbers)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        classifier_pipe = pipeline(
            "sentiment-analysis",
            model=self.model_name,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

        return classifier_pipe
    

    def _get_sentiment(self, text:str) -> Dict:
        """_summary_

        Args:
            text (str): _description_

        Returns:
            Dict: _description_
        """
        cls_pipeline = self.get_model_pipeline()
        sentiment = cls_pipeline(text)

        # print(f"Sentiment for index {index}: Label={sentiment[0]['label']}, Score={sentiment[0]['score']} ")
        return {
            'Sentence': text,
            'Label': sentiment[0]['label'],
            'Confidence': sentiment[0]['score']
        }


    def get_conversation_category(self, text) -> Dict :
        """_summary_

        Args:
            text (_type_): _description_

        Returns:
            Dict: _description_
        """
        sumtext_dict = defaultdict(str)
        # for now summarizing text only if sentence goes over the # of tokens the model is trained for. 
        if len(text.split()) > self.batch_size:
            text = self.summarize_text(self, text, num_sentences=self.num_sentences)
            sumtext_dict['SummarizedText'] = text

        text = self.lemmitize(text)
        sentiment:Dict = self.get_sentiment(text)
        sentiment.update(sumtext_dict)

        return sentiment


    def _update_with_sentiment(self, row):
        """Updates the given `row` with the sentiment Label along with the Confidence score. 
        It also includes SummarizedText, but value populated only if the original text was modified 
        to fit the model's constraints.

        Args:
            row (_type_): A Pandas DataFrame row

        Returns:
            _type_: Pandas DataFrame row with original data along with new columns 
            "SummarizedText", "Label" aka sentiment and "Confidence" score.
        """
        context_text = row['Context']
        sentiment:Dict = self.get_conversation_category(context_text)
        print(f"Sentiment for : Label={sentiment['Label']}, Confidence={sentiment['Confidence']} ")
        row['SummarizedText'] = context_text
        row['Label'] = sentiment['Label']
        row['Confidence'] = sentiment['Confidence']

        return row
    

    def get_conversation_categories(self, df: pd.DataFrame) -> pd.DataFrame :
        """Given a DataFrame consisting of column `Context`, the function identifies the sentiment of the 
        text in this column for each row and returns the sentiment value along with confidence score of this
        prediction and a summarized text if the original text is too long and had to be modified to process
        through the model.

        Args:
            df (pd.DataFrame): With all the texts to be processed under the column `Context`, in separate rows

        Returns:
            pd.DataFrame: Original dataframe with new columns "SummarizedText", "Label" aka Sentiment, "Confidence" 
        """
        df_sent = df.apply(self._update_with_sentiment, axis=1)
        # reorder cols given by default DF sorts by column names
        cols_order = ['Context', 'Response', 'SummarizedText', 'Label', 'Confidence']
        df_sent = df_sent[cols_order]

        return df_sent



def main():
    CSV_DATA_DIR = DATA_DIR + '/nlp-mental-health-conversations'

    # 
    dataset_url = 'https://www.kaggle.com/datasets/thedevastator/nlp-mental-health-conversations/data'
    od.download(dataset_url, data_dir=DATA_DIR)
    df:pd.DataFrame = pd.read_csv(CSV_DATA_DIR + '/train.csv')

    zero_txt_indexes = df[df['Response'] == '0'].index.tolist()
    df_clean = df.dropna()
    df_clean = df_clean.drop(index=zero_txt_indexes)

    model_name = "sid321axn/Bio_ClinicalBERT-finetuned-medicalcondition"
    # sentiment_model = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    categorizer = HealthConversationCategorizer(model_name=model_name)
    long_text:str = '''I'm a teenager, and throughout my entire life, I've never really had good parents, or parents at all for that matter. I'm not exaggerating. I was living with my mom and grandparents until my father, in prison for most of my life, got out when I was in middle school. His mom, my grandma, only lived a mile down the road from my mom’s house, and I was so awe-stricken with my dad that I got to stay with him for a long time. 
        Meanwhile, I did not realize that my mom was doing hardcore drugs. My mom went to prison for that and lost her café. We live in a very small town, so everyone knew about it, and I was bullied because of who my parents were. My dad ended up getting in with the wrong people and went back to prison. My mom and him had a mutual friend and often hung out at that person’s house. 
        My parents did not get along at this point. We were driving him home one day from this house, and my mom stopped the car and kicked him out. He got out of the car, went to the driver’s side, and punched my mom in the face. I got out and told him not to hit my mom. At that point, I was really scared and mad that he did that, so I ran towards him to stop him. He literally picked me up and threw me on the back of a gravel road. 
        I couldn't even walk. My mom tried to help me, but he started choking her. I hobbled over, and she barely got into the car, and we quickly drove away and called the police and ambulance. He was so badly strung out on drugs. He went to prison again and seems to be doing well. I met up with him once with my grandma, and we had coffee, but he's so hard to handle. I think a lot of it is that I can't bring myself to forgive him. 
        My mom went back to prison again for drugs, and while she was in there, I moved in with my dad’s mom (the one who lived just down the road) because I trust her, her house is stable, and she's more nurturing, understanding, and loving then my other grandparents. I also stay at my boyfriend’s a lot. Now that my mom is out of prison, she's trying to control every aspect of my life. 
        She’s trying to make me move back home out of Susan's house, and I don't want to. I don't like it there. They condone drug abuse and many other things, and I'm just not comfortable. She's even threatened to call the police and say I'm a runaway because she has custody of me. My boyfriend has always had this picture-perfect life, and his family are strict Christians. 
        One time, his mom even went as far as to say that if he and I break up, if we were having sex, I would say that he", "raped me. I've got so many problems I don't even know what to do.'''

    sentiment = categorizer.get_conversation_category(long_text)
    print("Sentiment: ", sentiment)

    # df_clean.to_csv(f"{DATA_DIR}/output/mental_health_convo_categ.csv")




    