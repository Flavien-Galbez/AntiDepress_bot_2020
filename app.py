# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 13:26:53 2020

@author: flavi
"""
from flask import Flask, request
from pymessenger.bot import Bot
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

# This one will be used in order give jokes to the user
JOKES_API = "" #no need key if we use a few of request (https://api.jokes.one/)

#This small part will use nltk library in order to autogenerate suggestion from a text from a page web. We made this with only one site but we can extand this implemantation at a large nuber of site.
#Firstly we have to reorder the site web formulation and tokenize its with nltk in order to analize its and create a good answers for our bot 
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
# We use autogenreates answer in the other case (cf following part)
# Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "hey")
GREETING_RESPONSES = ["hi", "hey", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

BYE_INPUTS = ("bye","goodbye")
BYE_RESPONSES = ["Bye !", "See you soon !", "Good luck ! Take care :) "]

def bye(sentence):
    """If user's input is a goodbye, return a goodbye response"""
    for word in sentence.split():
        if word.lower() in BYE_INPUTS:
            return random.choice(BYE_RESPONSES)

THANK_INPUTS = ("thank", "thanks")
THANK_REPONSES = ["You are welcome !", "It's a pleasure", "No problem"]

def thank(sentence):
    """If user's input is a thanks, return a thanks response"""
    for word in sentence.split():
        if word.lower() in BYE_INPUTS:
            return random.choice(BYE_RESPONSES)


URGENT_INPUTS = ("kill", "suicide", "murder", "help", "die")
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
FEELING_GOOD_RESPONSES = ["I'm happy to ear that ! Do you want a joke ?","Nice ! We can go ain for a joke if you want ?"]

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

#Permit to extract a joke from Jokes API
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
        # In some case the bot can't genertate an apropriate answer so we have to apologize x)
        chatbot_response=chatbot_response+"I am sorry! I don't understand you :("
        return chatbot_response
    else:
        chatbot_response = chatbot_response +sentence_list[similar_sentence_number]
        return chatbot_response

#In order to connect to Messenger

app = Flask(__name__)
ACCESS_TOKEN_FB = 'EAAL6b8iQeEoBAKJPYLoNCzNgcqzt2puf0SnUlvxS6WVoxZCyINwZBIZCmPR7OHgEEYBpMn4ZCkBZBOoBNjNyT2Lt3M8oIXLrFMwx4avx7aUObBNUEwAji3nn5ZCfZCRFSJJNV6JR5KhQAUK91yASiYEnGhNMDwhRb4cdc5mGmYjGOLkhZAZBkP9MS'
VERIFY_TOKEN_FB = 'DEPRESSBOTTOKENVERIF01'
bot = Bot(ACCESS_TOKEN_FB)


#Here the reception and transmission of message from facebook
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message(message['message'].get('text'))
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN_FB:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#Allow to select an apropiate answers
def get_message(user_response):
    user_response=user_response.lower()
    if(bye(user_response)!=None):
        if(thank(user_response)!=None):
            return(thank(user_response))
        else:
            if(greeting(user_response)!=None):
                return(greeting(user_response))
            elif(urgent(user_response)!=None):
                return(urgent(user_response))
            elif(feeling_bad(user_response)!=None):
                return(feeling_bad(user_response))
            elif(feeling_good(user_response)!=None):
                return(feeling_good(user_response))
            elif(type_joke(user_response)!=None):
                return(type_joke(user_response))
            elif(joke(user_response)!=None):
                return(joke(user_response))
            else:
                return(give_reply(user_response))
                sentence_list.remove(user_response)
    else:
        return (bye(user_response))

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()