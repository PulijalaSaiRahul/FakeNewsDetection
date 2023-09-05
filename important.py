import numpy as np
import string
import re
from nltk.corpus import stopwords
import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_session import Session
from flask_bootstrap import Bootstrap
import pickle
from titletest import *
import requests 
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import easyocr
from chatbot import chatBot
from PIL import Image
from contactmail import findMail
from urlsecurity import urlSecurity

app=Flask(__name__)
Bootstrap(app)

# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

newstitle_object = checkTitle("")
processes = [newstitle_object.spelling_mistakes, newstitle_object.classify_clickbait, newstitle_object.subjective_test, newstitle_object.is_newstitle, newstitle_object.present_on_google]
names = ['Checkingforspellingmistakes', 'Checkingforclickbaittitle', 'Checkingforsubjectivetitles', 'Checkingforvalidnewstitle', 'Checkingforwebavailability']
index = -1
pages = ['spellfail.html', 'clickfail.html', 'subjecfail.html', 'newtitilefail.html', 'availweb.html']
headline = ''
last_executed = True

def scrape_links(text):
    pattern = r'\b(?:(?:https?|ftp):\/\/|www\.)[-a-zA-Z0-9+&@#\/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#\/%=~_|]'
    links = re.findall(pattern, text)
    return links


def present_on_google_news_2(domain):
    print(domain)
    domain=domain.replace("www","")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    ggl_news_link = f"https://www.google.com/search?q={domain}&tbm=nws"
    req = requests.get(ggl_news_link, headers=headers)
    sup = BeautifulSoup(req.content, 'html.parser')
    link = sup.find('a', class_='WlydOe')
    if link:
        nd_domain = urlparse(link['href'])
        domain_name = nd_domain.netloc
        domain_name = domain_name.replace('www.', '')
        if domain in domain_name:
            return True
    return False


def is_url(text):
    pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(pattern, text) is not None

def checkbox_activate1():
    global processes
    global names
    global pages
    processes = [newstitle_object.classify_clickbait, newstitle_object.subjective_test, newstitle_object.is_newstitle, newstitle_object.present_on_google]
    names = ['Checkingforclickbaittitle', 'Checkingforsubjectivetitles', 'Checkingforvalidnewstitle', 'Checkingforwebavailability']
    pages = ['clickfail.html', 'subjecfail.html', 'newtitilefail.html', 'availweb.html']

def checkbox_activate2():
    global processes
    global names
    global pages
    processes = [newstitle_object.subjective_test, newstitle_object.present_on_google]
    names = ['Checkingforsubjectivetitles', 'Checkingforwebavailability']
    pages = ['subjecfail.html', 'availweb.html']

def checkbox_activate3():
    global processes
    global names
    global pages
    processes = [newstitle_object.present_on_google]
    names = ['Checkingforwebavailability']
    pages = ['availweb.html']

def checkbox_activate4():
    global processes
    global names
    global pages
    processes = [newstitle_object.spelling_mistakes, newstitle_object.subjective_test, newstitle_object.present_on_google]
    names = ['Checkingforspellingmistakes', 'Checkingforsubjectivetitles', 'Checkingforwebavailability']
    pages = ['spellfail.html', 'subjecfail.html', 'availweb.html']

def set_all():
    global processes
    global names
    global index
    global pages
    global headline
    global newstitle_object
    headline = ''
    newstitle_object = checkTitle("")
    processes = [newstitle_object.spelling_mistakes, newstitle_object.classify_clickbait, newstitle_object.subjective_test, newstitle_object.is_newstitle, newstitle_object.present_on_google]
    names = ['Checkingforspellingmistakes', 'Checkingforclickbaittitle', 'Checkingforsubjectivetitles', 'Checkingforvalidnewstitle', 'Checkingforwebavailability']
    index = -1
    pages = ['spellfail.html', 'clickfail.html', 'subjecfail.html', 'newtitilefail.html', 'availweb.html']


@app.route('/')
def home():
    global index
    global headline
    headline = ''
    index = -1
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/detect',methods=['POST','GET'])
def detect():
    global headline
    set_all()
    if request.method=='POST':
        
        input_text = request.form.get('text')
        if 'image' in request.files:
            input_image = request.files['image']
        input_url = request.form.get('texturl')
        
        if input_text != None:
            print(input_text)
            headline = input_text
            checkbox1 = request.form.get('check1')
            checkbox2 = request.form.get('check2')
            if checkbox1:
                checkbox_activate1()
            if checkbox2:
                checkbox_activate2()
            if headline == '':
                headline = input_text
                newstitle_object.headline = headline
            links = scrape_links(input_text)
            if len(links):
                for i in links:
                    if urlSecurity(i) == False:
                        return render_template("mal.html")
            return redirect(url_for('given_is_text', text=input_text, progress_name=names[0], num = 1))
        
        elif input_url != None:
            if is_url(input_url) == False:
                print("Please enter valid url")
            try:
                req = requests.get(input_url)
            except:
                print("The Website is not accessible")
            soup = BeautifulSoup(req.content, 'html.parser')
            text = soup.find('h1')
            print(text)
            if text == None:
                print("the given website has no Headline text, please avoid using social media website urls")
            nd_domain = urlparse(input_url)
            domain_name = nd_domain.netloc
            if present_on_google_news_2(domain_name) == False:
                print("the given domain is not present on google news, Please give only news websites url, if a news website is not present on google news there is a high possibility that the news pubished by that specific news website if fake")
            checkbox_activate3()
            if headline == '':
                headline = text.text
                print(headline)
                newstitle_object.headline = headline
            return redirect(url_for('given_is_text', text=headline, progress_name=names[0], num = 1))
        
        elif input_image != None:
            checkbox4 = request.form.get('check4')
            temp_path = 'images/image.jpg'
            input_image.save(temp_path)
            x = int(float(request.form['x']))
            y = int(float(request.form['y']))
            width = int(float(request.form['width']))
            height = int(float(request.form['height']))
            print(x,y,width, height)
            img = Image.open(temp_path)
            cropped_img = img.crop((x, y, x + width, y + height))
            cropped_img = cropped_img.convert('RGB')
            cropped_img.save('images/cropped_image.jpg')
            reader = easyocr.Reader(['en'])
            result = reader.readtext('images/cropped_image.jpg')
            extracted_text = [entry[1] for entry in result]
            x = ''
            x=' '.join(extracted_text)
            if x == '':
                print("please input images containing text")
            checkbox_activate4()
            if checkbox4:
                checkbox_activate2()
            if headline == '':
                headline = x
                newstitle_object.headline = headline
            
            return redirect(url_for('given_is_text', text=x, progress_name=names[0], num = 1))

    return render_template('detect.html')

@app.route('/truenews',  methods=['GET', 'POST'])
def true_news():
    
    return render_template("true_news.html", link=newstitle_object.recom_link)

@app.route('/autopopulate', methods=['GET', 'POST'])
def autopopulate():
    url = request.json.get('url')
    print(url)
    findMail(url, newstitle_object.article + f"\n{newstitle_object.recom_link}+\n" ,newstitle_object.headline).run()
    return jsonify({'yes': True})


@app.route('/listen')
def listen():
    global index
    global headline
    index+=1
    newstitle_object.headline = headline
    val = processes[index]()
    print(val)
    if val == True:
        return jsonify({'value': True})
    else:
        return jsonify({'value': False})
    
@app.route('/chatbot/<string:question>')
def chatbot(question):
    print(question)
    cb = chatBot()
    if question:
        answer = cb.get_answer(question)
    return jsonify({'answer': answer})
    

@app.route('/progress/<string:text>/<string:progress_name>/<int:num>', methods=['GET', 'POST'])
def given_is_text(text, progress_name, num):
    global last_executed
    global headline
    global names
    global pages
    print(num)
    if num == 0:
        page = pages[names.index(progress_name)]
        return render_template(page)
    else:
        ind = names.index(progress_name)

        if progress_name=='Checkingforspellingmistakes':
            return render_template('new.html', input_data="Checking if given text contains any spelling mistakes", my_list=names)
        if progress_name=='Checkingforclickbaittitle':
            return render_template('new.html', input_data="Checking for clickbait title in given text", my_list=names)
        if progress_name=='Checkingforsubjectivetitles':
            return render_template('new.html', input_data="Checking the given text is Subjective or Objective", my_list=names)
        if progress_name=='Checkingforvalidnewstitle':
            return render_template('new.html', input_data="Checking the given textis Valid News Title or Not", my_list=names)
        if progress_name=='Checkingforwebavailability':
            return render_template('new.html', input_data="Checking the availability of given news in the Web", my_list=names)

@app.route('/similar')
def similar():
    global newstitle_object
    print(newstitle_object.max_similarity)
    return jsonify({"similar": int(newstitle_object.max_similarity * 100)})

@app.route('/predict',methods=['POST'])
def predict():
    if request.method=='POST':
        input_text=request.form.get('text')
        if input_text:
            print("hello"+input_text)
    test=request.form.values()
    test_ser=pd.Series(test)
    return render_template('detect.html',prediction_text='Given News is {}!'.format('true'),result="RESULT:")

@app.route('/names')
def names():
    global names
    num = 1
    if len(names) == 5:
        num = 1
    if len(names) == 4:
        num = 2
    if len(names) == 2:
        num = 3
    if len(names) == 1:
        num = 4
    if len(names) == 3:
        num = 5
    return jsonify({'number':num})


if __name__=='__main__':
    app.run(debug=True,ssl_context="adhoc")