import nltk 
from nltk import word_tokenize, pos_tag, pos_tag_sents
from nltk.stem.wordnet import WordNetLemmatizer
import datetime
import time
import random
from googleapiclient.discovery import build
from flask import Flask, render_template
from langdetect import detect
from flask_socketio import SocketIO, emit


app = Flask(__name__)
nltk.download('tagsets')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def get_text(text):
    key_words = preprocessing_data(text)
    urls = []
    for word in key_words:
        urls.append(image_search(word))
    return urls

def image_search (query):
    cx = "008972884188395970079:loopwvxlbyi"
    key = "AIzaSyCAfFiWIqxOdVQkOsqm3TDuRpukuFpA1zc"
    start_time = time.time()
    
    service = build("customsearch", "v1",
               developerKey=key)
    
    res = service.cse().list(
         q=query,
         cx=cx,
         searchType='image',
         rights='cc_publicdomain cc_attribute cc_sharealike cc_noncommercial cc_nonderived',
         fileType='png',
         num = 10,
       ).execute()
    
    
    url = res['items'][random.randint(0, 9)]['link']
    print(url)
    print("--- %s seconds ---" % (time.time() - start_time))
    return url

def preprocessing_data(text):
    trash_words = ['hello', 'hi', 'there', 'here', 'my', 'mine', 'your', 'yours', 'do', 'did']
    lmtzr = WordNetLemmatizer()
    lang = "en"

    if (detect(text) == 'uk' or detect(text) == 'ru'):
        lang = "rus"

    # cleaning data
    text = text.replace(',', '').replace('.', '').replace('?', '').replace('!', '').replace(')', '').replace('(', '').split()
    message = [word for word in text if word.lower() not in trash_words]
    message = [lmtzr.lemmatize(word) for word in message]

    # get only nouns or noun phrases
    print (lang)
    if (lang == "en"):
        parsed_message = [word[0] for word in pos_tag(message, lang = lang) if word[1] == 'NN' or word[1] == 'NNP']
    else:
        parsed_message = [word[0] for word in pos_tag(message, lang = lang) if word[1] == 'S']

    answer = []
    for word in parsed_message:
        answer.append(time_word(word))

    # remove duplicates
    answer = list(set(answer))

    return answer

def time_word(word):
    time_words = ['yesterday', 'today', 'tomorrow']
    months = {1: 'january', 2: 'february', 3: 'march', 4: 'april', 5: 'may', 6: 'june', 7: 'july', 8: 'august', \
              9: 'september', 10: 'october', 11: 'november', 12: 'december'}
    
    word = word.lower()
    if word not in time_words:
        return word
    else: 
        if word == 'today':
            dt = datetime.datetime.now()
        elif word == 'tomorrow':
            dt = datetime.date.today() + datetime.timedelta(days=1)
        else:
            dt = datetime.date.today() - datetime.timedelta(days=1)
        return "%s %s" % (str(dt.day), months[dt.month])

@app.route('/')
def index():
    return 'index.html'

@socketio.on('firstConnect')
def handleMessage(msg):
    print ("# User Connected ...")
    
@socketio.on('getImage')
def message(msg):
    print("I GET A MESSAGE: " +  msg)
    imgUrls = get_text(msg)
    emit('imageResponse', {'data': imgUrls[0]})

if __name__ == '__main__':
    socketio.run(app)
