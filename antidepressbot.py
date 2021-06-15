# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 22:06:16 2020

@author: flavi
"""
import bs4 as bs  
import urllib.request  
import re
import nltk
import random
import string # to process standard python strings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
import requests
import urllib
import warnings
warnings.filterwarnings("ignore")

JOKES_API = "" #no need if we use a few of request (https://api.jokes.one/)
raw_data = urllib.request.urlopen('https://kidshealth.org/en/teens/suicide.html')  
raw_data = raw_data.read()
 
html_data = bs.BeautifulSoup(raw_data,'lxml')
 
all_paragraphs =html_data.find_all('p')
 
article_content = ""
 
for p in all_paragraphs:  
    article_content += p.text
    
article_content =  article_content.lower()# converts to lowercase
 
article_content  = re.sub(r'\[[0-9]*\]', ' ', article_content )  
article_content = re.sub(r'\s+', ' ', article_content )  
 
sentence_list = nltk.sent_tokenize(article_content)  
article_words= nltk.word_tokenize(article_content )
 
nltk.download('punkt') 
nltk.download('wordnet') 
 
 
lemmatizer = nltk.stem.WordNetLemmatizer()
 
def LemmatizeWords(words):
    return [lemmatizer.lemmatize(word) for word in words]
 
remove_punctuation= dict((ord(punctuation), None) for punctuation in string.punctuation)
 
def RemovePunctuations(text):
    return LemmatizeWords(nltk.word_tokenize(text.lower().translate(remove_punctuation)))
 

# These part permit to the bot to work in usual case and be sure to help in crisis cases

# Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

URGENT_INPUTS = ("suicide", "need help", "die")
URGENT_RESPONSES = ["Please call the 1-800-273-8255, they can help you"]

def urgent(sentence):
    """If user's input is realy dangerous for himself, return a number to help him"""
    for word in sentence.split():
        if word.lower() in URGENT_INPUTS:
            return random.choice(URGENT_RESPONSES)

FEELING_BAD_INPUTS = ("bad","sad", "disastrous", "depressive", "need help")
FEELING_BAD_RESPONSES = ["I'm sad for you, I can give you a joke too make you more happy.", "Sad ... I'm a pro joker if it can help.","Let's go for a joke ? I'm sure that it can help you to feel better"]

def feeling_bad(sentence):
    """If user's input is a bad feeling, return a response to help"""
    for word in sentence.split():
        if word.lower() in FEELING_BAD_INPUTS:
            return random.choice(FEELING_BAD_RESPONSES)

FEELING_GOOD_INPUTS = ("nice", "happy", "fine", "excellent", "handsome", "good")
FEELING_GOOD_RESPONSES = ["I'm happy to ear that ! Do you want a joke ?","Nice ! We can go again for a joke if you want ?"]

def feeling_good(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in FEELING_GOOD_INPUTS:
            return random.choice(FEELING_GOOD_RESPONSES)

JOKE_INPUTS = ("joke", "yes", "go")
JOKE_RESPONSES = ["Which kind of jokes ? Got the type of : anykind, knock-knock, animal, blonde","Which type of jokes ? Got the type of : anykind, knock-knock, animal, blonde"]


def joke(sentence):
    """If user's input is a call of joke, return a response to choose what type"""
    for word in sentence.split():
        if word.lower() in JOKE_INPUTS:
            return random.choice(JOKE_RESPONSES)

# These part permit to the bot to give a joke to the user thanks to the Jokes API

TYPE_JOKE_INPUTS = ("anykind","jokeoftheday","knock-knock","knock","animal","blonde")

def get_joke(joketype):
    url = 'https://api.jokes.one/jod?category='+joketype
    headers = {'content-type': 'application/json',
	   'X-JokesOne-Api-Secret': format(JOKES_API)}
    response = requests.get(url, headers=headers)
    jokes=response.json()['contents']['jokes'][0]
    return(jokes['joke']['text'])
    
def type_joke(sentence):
    """If user's input is a type of joke, return a joke of this type"""
    for word in sentence.split():
        if word.lower() in TYPE_JOKE_INPUTS:
            if word.lower() == "knock-knock" or word.lower() == "knock" :
                return get_joke("knock-knock")
            elif word.lower() == "animal" :
                return get_joke("animal")
            elif word.lower() == "blonde" :
                return get_joke("blonde")
            else :
                return get_joke("")


# These part autogenerate reponse with nltk from a website which provide help for peaple who want to commit a suicide
# In the case of the bot doesn't match a response on the site he say "I am sorry! I don't understand you :("

def give_reply(user_input):
    chatbot_response=''
    sentence_list.append(user_input)
    word_vectors = TfidfVectorizer(tokenizer=RemovePunctuations, stop_words='english')
    vecrorized_words = word_vectors.fit_transform(sentence_list)
    similarity_values = cosine_similarity(vecrorized_words[-1], vecrorized_words)
    similar_sentence_number =similarity_values.argsort()[0][-2]
    similar_vectors = similarity_values.flatten()
    similar_vectors.sort()
    matched_vector = similar_vectors[-2]
    if(matched_vector ==0):
        chatbot_response=chatbot_response+"I am sorry! I don't understand you :("
        return chatbot_response
    else:
        chatbot_response = chatbot_response +sentence_list[similar_sentence_number]
        return chatbot_response


flag=True
print("BOTY: My name is Boty, the kind robot. I'm here to help you. If you want to exit, type \"Bye\" !")
while(flag==True):
    user_response = input("HUMAN : ")
    print()
    user_response=user_response.lower()
    if(user_response!='bye'):
        if(user_response=='thanks' or user_response=='thank' ):
            flag=False
            print("BOTY: You are welcome..")
        else:
            if(greeting(user_response)!=None):
                print("BOTY: "+greeting(user_response))
            elif(urgent(user_response)!=None):
                print("BOTY: "+urgent(user_response))
            elif(feeling_bad(user_response)!=None):
                print("BOTY: "+feeling_bad(user_response))
            elif(feeling_good(user_response)!=None):
                print("BOTY: "+feeling_good(user_response))
            elif(type_joke(user_response)!=None):
                print("BOTY: "+type_joke(user_response))
            elif(joke(user_response)!=None):
                print("BOTY: "+joke(user_response))
            else:
                print("BOTY: ",end="")
                print(give_reply(user_response))
                sentence_list.remove(user_response)
    else:
        flag=False
        print("BOTY: Bye! take care..")