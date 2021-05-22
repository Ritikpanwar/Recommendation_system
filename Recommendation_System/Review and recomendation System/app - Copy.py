# -*- coding: utf-8 -*-

import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from flask import Flask, request, render_template
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import csv


app = Flask(__name__)
model=tf.keras.models.load_model('my_model_4.h5').decode()
tokens=pd.read_csv("embd.csv")
tokens=tokens.iloc[:10001,:]
token={}
for i,j in zip(tokens['keys'],tokens['values']):
    token[i]=j
with open('review-result.csv', 'w', newline = '', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'verified', 'review'])
df = pd.DataFrame()
# selenium functions
def get_url(search_term):
    """Genrate a url from search term"""
    template = "https://www.amazon.com/s?k={}"
    search_term = search_term.replace(" ","+")
    
    #add term query to url
    url = template.format(search_term)
    
    #add page query placeholder
    url += "&page={}"
    
    return url

def extract_record(item):
    """Extract and return data from a single record"""
    
    try:
        #description and url
        atag = item.h2.a
        desc = atag.text.strip()
        url = 'https://www.amazon.com' + atag.get('href')
    except AttributeError:
        return
    
    try:
        #price
        price_parent = item.find('span','a-price')
        price = price_parent.find('span', 'a-offscreen').text
    except AttributeError:
        return
    
    try:
        #rank and rating
        rating = item.i.text
        review_count = item.find('span',{'class': 'a-size-base', 'dir': 'auto'}).text
    except AttributeError:
        rating = ''
        review_count = ''
    
    result = (desc, price, rating, review_count, url)
    return result

def pmain(search_term):
    """Run main program routine"""
    # stratup the webdriver
    driver_path = 'chromedriver.exe'
    driver = webdriver.Chrome(driver_path)
    
    records = []
    url = get_url(search_term)
    
    for page in range(1,21):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for itm in results:
            record = extract_record(itm)
            if record:
                records.append(extract_record(itm))
    driver.close()
    #save data to csv file
    with open('result.csv', 'w', newline = '', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['desc', 'price', 'rating', 'review_count', 'Url'])
        writer.writerows(records)
# seelenuium function end
def r_get_url():
    """Genrate a url from search term"""
    template = data.Url[0]
    url = template.replace("dp","product-reviews")+'&pageNumber={}'+'&sortBy=recent'
    
    return url

def r_extract_record(item):
    """Extract and return data from a single record"""
    stop = 1
    try:
        #review date
        date = item.find('span',{'data-hook':'review-date'}).text
        if int(date[-4:])<2020:
            stop = 0
        
    except AttributeError:
        return 
    
    try:
        #review
        review = item.find('span',{'data-hook':'review-body'}).text
    except AttributeError:
        return
    
    try:
        #verify purchase
        verified = item.find('span',{'data-hook':'avp-badge'}).text
    except AttributeError:
        return
    
    result = (date, verified, review)
    return result, stop

def r_main():
    """Run main program routine"""
    # stratup the webdriver
    driver_path = 'chromedriver.exe'
    driver = webdriver.Chrome(driver_path)
    url = r_get_url()
    records = []
    stop = 1
    page=0
    while stop==1:
        page+=1
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-hook': 'review'})
        for itm in results:
            r = r_extract_record(itm)
            
            if r:
                stop = r[-1]
                records.append(r[0])
    driver.close()
    
    #save data to csv file
    with open('review-result.csv', 'a', newline = '', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(records)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    global df

    input_features = [x for x in request.form.values()]
    pmain(input_features)
    df=pd.read_csv("result.csv")
    for i in range(min(10,df.shape[0])):
        r_main(df["Url"][i])
        
    
    #validate input hours
    dfreview=pd.read_csv(review-result.csv)  
    countp=0
    for i in range(dfreview.shape[0]):
        output = model.predict(dfreview[review][i])
        if(output=="Positive"):
            countp=countp+1
    countn=dfreview.shape[0]-countp

    # input and predicted value store in df then save in csv file

    return render_template('index.html', prediction_text='Total review= {}, Positive review= {}, Negative review ={} '.format(dfreview.shape[0], countp,countn)


if __name__ == "__main__":
   # app.run(host='0.0.0.0', port=8080)
    app.run()