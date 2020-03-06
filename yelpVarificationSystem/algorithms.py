# Importing Libraries
import os
import re
import ast
import csv
import sys
import nltk
import json
import time
import random
import requests
import selenium
import subprocess
import pandas as pd
import numpy as numpy
from random import randrange
from xvfbwrapper import Xvfb
from bs4 import BeautifulSoup as bs
from googletrans import Translator
from time import sleep
import datetime as DT
import selenium

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, 'config.json')) as config_file:
    config = json.load(config_file)

# Importing Library Data 
nltk.data.path.append(config['NLTK_PATH'])
nltk.download('vader_lexicon', download_dir=config['NLTK_PATH'])
nltk.download('punkt', download_dir=config['NLTK_PATH'])
from nltk import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Global Variables
username=''
date=[]
rating =[]
review = []
entity =[]
userID=[]
userData =[]
name=[]
nae=[]
user_ID=[]
choice_checker=[]
check = ["?","/","!"]
flag = False
message=''

class Algorithms():

# Text Tokenization
    def wordTokenizeText(self, review):
        tokens = review.lower()                               # Lower the text.
        tokens = word_tokenize(tokens)                        # Split into words.
        #tokens = [w for w in tokens if not w in stop_words]   # Remove stopwords.
        tokens = [w for w in tokens if w.isalpha()]           # Remove numbers and punctuation.
        return tokens

# Calcualting jaccard similarity coeffeicient 
    def jaccardSimilarity(self, review1, review2):
        '''
        Find the commanility between vocabularies used within two texts
        '''
        intersection = set(review1).intersection(set(review2))
        union = set(review1).union(set(review2))
        return len(intersection)/len(union)
    
# Calculate the probabilities of Yelp reviewers being fake, bot or authentic
    def calculateYelpReviewProbabilities(self):
        if userData:
            userDataFrame = pd.DataFrame(userData)
            # Cleaning Data
            userDataFrame = userDataFrame[['userID', 'comment']]
            userDataFrame = userDataFrame.drop_duplicates().reset_index(drop = True)
            # Sentiment Analysis
            sid = SentimentIntensityAnalyzer()
            userDataFrame["sentiments"] = userDataFrame["comment"].apply(lambda x: sid.polarity_scores(x))
            userDataFrame = pd.concat([userDataFrame.drop(['sentiments'], axis=1), userDataFrame['sentiments'].apply(pd.Series)], axis=1)
            # Conditions For Sentiment Classification
            sentiment_score = []
            for s in userDataFrame['compound']:
                # when sentiment is too positive or negative
                if s < -0.99 or s > 0.99:
                    sentiment_score.append(1.0)
                # when sentiment is very positive or negative
                elif s < -0.8 or s > 0.8:
                    sentiment_score.append(0.75)
                # when sentiment is just positive or negative
                elif s < -0.6 or s > 0.6:
                    sentiment_score.append(0.5)
                # when sentiment is neutral
                else:
                    sentiment_score.append(0.0)
            # Create sentiment score column
            userDataFrame['sentiment_score'] = sentiment_score
            # Probability Calculate
            d = dict(userDataFrame.sentiment_score.value_counts())
            if 1 in d:
                probabilityOfPaid = d[1]/sum(d.values())
            else:
                probabilityOfPaid = 0.0
            probabilityOfHuman = 1- probabilityOfPaid
            # BOT DETECTION JACCARD SIMILARITY
            userDataFrame['comment'] = userDataFrame['comment'].apply(self.wordTokenizeText)
            summation = 0
            count = 0
            corpus = userDataFrame['comment']
            length = len(corpus)
            for i in range(length-1):
                for j in corpus[i+1: ]:
                    summation += self.jaccardSimilarity(corpus[i], j)
                    count+= 1
            botScore = summation/count
        else:
            # Set default values
            probabilityOfPaid=0
            probabilityOfHuman=0
            botScore = 0
            probabilityOfBot=0
        if (botScore>0 or probabilityOfHuman>0 or probabilityOfPaid>0):
            total = probabilityOfHuman + probabilityOfPaid + botScore
            probabilityOfHuman = round((probabilityOfHuman / total), 3)
            probabilityOfPaid = round((probabilityOfPaid / total), 3)
            probabilityOfBot = round((botScore / total), 3)
        return probabilityOfHuman, probabilityOfPaid, probabilityOfBot

# Calculate the probabilities of Amazon product being fake, bot or authentic
    def calculateAmazonReviewProbabilities(self):
        if userData:
            # Read amazon data from database
            userDataFrame = pd.read_csv(config['user_db_am'])
            # Cleaning Data
            userDataFrame.columns=['ID','reviewer', 'review','Status']
            userDataFrame['review'] = userDataFrame['review'].apply(lambda x : ast.literal_eval(x))
            # Caclulate sentiment scores
            sid = SentimentIntensityAnalyzer()
            probabilityOfHuman = []
            probabilityOfPaid = []
            for r in userDataFrame['review']:
                polarity_score = pd.Series(r).apply(lambda x: sid.polarity_scores(x))
                polarityScoreCompound = [c['compound'] for c in polarity_score]
                sentiment_score = []
                for s in polarityScoreCompound:
                    # when sentiment is too positive or negative
                    if s < -0.90 or s > 0.90:
                        sentiment_score.append(1.0)
                    # when sentiment is very positive or negative
                    elif s < -0.8 or s > 0.8:
                        sentiment_score.append(0.75)
                    # when sentiment is just positive or negative
                    elif s < -0.6 or s > 0.6:
                        sentiment_score.append(0.5)
                    # when sentiment is neutral
                    else:
                        sentiment_score.append(0.0)
                # Probability calculate
                d = dict(pd.Series(sentiment_score).value_counts())
                if 1 in d:
                    paid = d[1]/sum(d.values())
                    probabilityOfPaid.append(paid)
                else:
                    paid = 0.0
                    probabilityOfPaid.append(paid)
                probabilityOfHuman.append(1 - paid)
        else:
            probabilityOfHuman=0
            probabilityOfPaid=0
        if (sum(probabilityOfHuman)>0 or sum(probabilityOfPaid)>0):    
            probabilityOfHuman = sum(probabilityOfHuman)/len(probabilityOfHuman)
            probabilityOfPaid= sum(probabilityOfPaid)/len(probabilityOfPaid)

        print(probabilityOfHuman,probabilityOfPaid)
        return probabilityOfHuman, probabilityOfPaid

# Calculate the probabilities of Facebook page being fake or authentic
    def calculateFacebookReviewProbabilities(self):
        # Read facebook data from database
        userDataFrame = pd.read_csv(config['user_db_fb'])
        # Cleaning Data
        userDataFrame.columns=['ID','name', 'star','Comment-box','Date','Status']
        userDataFrame['Date'] = userDataFrame['Date'].astype('datetime64[ns]')
        df1=userDataFrame.sort_values('Date')
        df1 = df1.reset_index(drop=True)
        # Calculate sentiment scores
        score = df1['Comment-box']
        rt =[]
        negative=[]
        positive=[]
        netural= []
        compound=[]
        analyser = SentimentIntensityAnalyzer()
        for i in range(len(score[1])):
            snt = analyser.polarity_scores(score[1][i])
            rt.append(snt)
            positive.append(snt['pos'])
            negative.append(snt['neg'])
            netural.append(snt['neu'])
            compound.append(snt['compound'])
        starscore=zip(negative,positive,netural,compound)
        df2 = pd.DataFrame(starscore, columns=['Negative_scores','Positive_scores','Netural_scores','Compound_scores'])
        #merging two dataframe by columns
        df_new = pd.concat([df1, df2], axis=1)
        #creating Dataframe d5 for date and star because we transform star data as integer and we did it for getting how many 5 stars in a sudden period
        df4=df_new['Date']
        df3= df_new['star'].astype(int)
        print(df3)
        df5=pd.concat([df4,df3],axis=1)
        #cleaning dataset and keeping just 5 stars
        df5=df5[df5.star>4]
        #time period setting for 5 days and counting how many 5 stars
        df5.set_index('Date', inplace = True)
        df6=df5.resample("2D").count()
        #sorting?cleaning data basis on count>24 of 5 stars
        df7=df6[df6.star>24]
        if len(list(df7['star'])) > 0:
            message = "Boosted Page"
        else: message = "Page is okay!"
        print("MESSAGE: ",message)
        return message

# Google functionality under construction

# Process yelp reviews (scraping, data cleaning, data storage)
    def yelpReviewProcess(self,username):
        # Refresh variables
        userData.clear()
        date.clear()
        rating.clear()
        review.clear()
        entity.clear()
        userID.clear()
        notFound=''
        # Clean punction marks 
        if any(ext in username for ext in check):
            pass
        else:
            user_exist = False
            # Check if previous yelp data exists
            if os.path.isfile(config['user_db_yelp']) == True :
                with open(config['user_db_yelp'],"r", encoding="utf-8") as database: 
                    database = csv.reader(database, delimiter=',')
                    counter = 0 #check if user exists in database 
                    name.clear()
                    # Create dictionary format for fetching data from database
                    for row in database:
                        if username == row[1]:
                            name.append(row[0])
                            userData.append({
                                'name': row[0],
                                'userID':row[1],
                                'rated':row[2],
                                'rating':row[3],
                                'comment':row[4],
                                'date':row[5],
                                'status':row[6] # DEV_TEST
                            })
                            user_exist= True
            else:
                # If no yelp data exists in database, create database first
                with open(config['user_db_yelp'], mode = 'w',encoding='utf-8') as database:
                    database = csv.writer(database, delimiter=',')
            if user_exist == False:
                # Since no data exists, scrape reviews from yelp
                # Build hyperlink
                userID_1 ='https://www.yelp.com/user_details_reviews_self?userid=' + username
                userID_2 = userID_1 + '\&rec_pagestart=10' 
                # Number of pages to scrape. For testing purpose we have gone upto first 2 pages
                links =[userID_1,userID_2]
                name.clear()
                for link in links:
                    #----------------------- Scrape Web Using Scrapy ------------------------------------------------#
                    # Scrapy Folder with Spider located from current directory. /reviewScrapper/reviewScrapper
                    # Command to activate scrapper: scrapy crawl tester -a start_url="url" -o user_db.csv
                    # Change directory to reviewScrapper
                    os.chdir(config['chdir_scrapper'])
                    # Make terminal URL for call. Create database as user_db
                    cmd = "scrapy crawl tester -a start_url="+link+" -o "+ config['user_db_yelp']
                    # Call subprocess to execute command line
                    proc = subprocess.Popen([cmd], shell=True)
                    time.sleep(3) # <-- sleep 
                    proc.terminate() # <-- terminate the process
                    time.sleep(3) # <-- sleep
                    # Change back to original directory
                    os.chdir(config['chdir_org'])
                    # Randomly delay scrapper
                    randTime = randrange(1,2)            
                    sleep(randTime)
                # From the database file, create a dictionary to form dataframe for probability calculation
                if os.path.isfile(config['user_db_yelp']) == True :
                    with open(config['user_db_yelp'],"r", encoding="utf-8") as database: 
                        database = csv.reader(database, delimiter=',')          
                        name.clear()
                        for row in database:
                            if username == row[1]:
                                name.append(row[0])
                                userData.append({
                                    'name': row[0],
                                    'userID':row[1],
                                    'rated':row[2],
                                    'rating':row[3],
                                    'comment':row[4],
                                    'date':row[5],
                                    'status':row[6] # DEV_TEST
                                })
                else:
                    # If no data on user is found while scraping
                    with open(config['user_db_yelp'], mode = 'w',encoding='utf-8') as database:
                        pass   
 
# Process amazon reviews (scraping, data cleaning, data storage)
    def amazonReviewProcess(self,username):
        # Refresh variables
        review = []
        userData.clear()
        date.clear()
        rating.clear()
        review.clear()
        entity.clear()
        userID.clear()
        notFound=''
        xvfb = Xvfb()
        if os.path.isfile(config['user_db_am']) == True :
            with open(config['user_db_am'],"r", encoding="utf-8") as database: 
                database = csv.reader(database, delimiter=',')
                counter = 0 #check if user exists in database 
                name.clear()
                # From database create dictionary and append to userData
                for row in database:
                    if username == row[0]:
                        name.append(row[0])
                        userData.append({
                            'ID': row[0],
                            'reviewer':row[1],
                            'review':row[2],
                            'Status':row[3],
                        })
                        counter = counter + 1
        else:
            with open(config['user_db_am'], mode = 'w',encoding='utf-8') as database:
                counter = 0
        if counter == 0:
            try:
                # Create window-less chrome
                xvfb.start()
                product_url = username
                # Create hyperlink
                reviews_url = product_url.replace("/dp", "/product-reviews")
                from selenium import webdriver
                from selenium.webdriver import Chrome

                from selenium.webdriver.chrome.options import Options

                options = Options()
                
                options.add_argument("--headless") # Runs Chrome in headless mode.
                options.add_argument('--no-sandbox') # # Bypass OS security model
                options.add_argument('--disable-dev-shm-usage')
                browser = webdriver.Chrome(chrome_options=options, executable_path=config['chromedriver'])
                # Fetch page information
                browser.get(reviews_url)
                try:
                    # Fetch specific information
                    # Get into the reviews section
                    reviewer_urls = browser.find_element_by_class_name('reviews-content').find_elements_by_class_name('a-spacing-mini')
                    reviewer_urls = [r.find_element_by_css_selector('a').get_attribute('href') for r in reviewer_urls][0::3]
                    userDataFrame = pd.DataFrame(columns = ['ID','reviewer', 'review','Status'])
                    with open(config['user_db_am'], mode = 'a', encoding='utf-8') as database:
                        database = csv.writer(database, delimiter=',')
                        for reviewer_link in reviewer_urls:
                            browser.get(reviewer_link)
                            # Dynamic, scroll down to load full (or most) content
                            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
                            browser.execute_script(scroll_down)
                            time.sleep(1)
                            # Get user name
                            reviewer_name = browser.find_element_by_class_name('name-container').find_element_by_css_selector('span').text
                            reviews = browser.find_elements_by_class_name('profile-at-content')
                            reviews_links = []
                            # Get reviews
                            for review in reviews:
                                review_link = review.find_element_by_css_selector('a').get_attribute('href')
                                if '/customer-reviews/' in review_link:
                                    reviews_links.append(review_link)
                                if len(reviews_links) == 20:
                                    break
                            urls = reviews_links[0:20]
                            l = []
                            for url in urls:
                                browser.get(url)
                                l.append(browser.find_element_by_class_name('review-text-content').find_element_by_css_selector('span').text)
                            # Append in the dataframe as a new row
                            row = [username,reviewer_name, l,0]
                            database.writerow(row)
                            userData.append({
                                    'ID': row[0],
                                    'reviewer':row[1],
                                    'review':row[2],
                                    'Status':row[3],
                                })
                            userDataFrame.loc[len(userDataFrame)] = row
                except:
                    userID.clear()
                    userID.append("No Reviews On This Product")

                browser.close()
                xvfb.stop()
            except OSError:
                print(
                    'Error: xvfb cannot be found on your system, please install '
                    'it and try again')
                exit(1)

# Process facebook reviews (scraping, data cleaning, data storage)
    def facebookReviewProcess(self,username):
        # Refresh variables
        date=[]
        userData.clear()
        date.clear()
        rating.clear()
        review.clear()
        entity.clear()
        userID.clear()
        notFound=''
        userData.clear()
        xvfb = Xvfb()
        # If file exists in database, fetch data and form dictionary
        if os.path.isfile(config['user_db_fb']) == True :
            with open(config['user_db_fb'],"r", encoding="utf-8") as database: 
                database = csv.reader(database, delimiter=',')
                counter = 0 #check if user exists in database 
                name.clear()
                for row in database:
                    if username == row[0]:
                        name.append(row[0])
                        userData.append({
                            'ID': row[0],
                            'name':row[1],
                            'star':row[2],
                            'Status':row[3],
                        })
                        counter = counter + 1
        else:
            with open(config['user_db_fb'], mode = 'w',encoding='utf-8') as database:
                counter = 0
        if counter == 0:
            try:
                # Start headerless chrome
                xvfb.start()
                # Customize link. Need to edit depending on various types of user input.
                if '/reviews/' not in username:
                    username = username+'/reviews/?ref=page_internal'
                from selenium import webdriver
                from selenium.webdriver import Chrome

                from selenium.webdriver.chrome.options import Options

                options = Options()
                
                options.add_argument("--headless") # Runs Chrome in headless mode.
                options.add_argument('--no-sandbox') # # Bypass OS security model
                options.add_argument('--disable-dev-shm-usage')
                browser = webdriver.Chrome(chrome_options=options, executable_path=config['chromedriver'])
                browser.get(username)
                try:
                    # Scroll Facebook Page
                    print("Selenium started")
                    scroll_down_1 = "window.scrollTo(0, 1000);"
                    scroll_down_2 = "window.scrollTo(1001, document.body.scrollHeight);"
                    # Scroll ratio: 4
                    for i in range(4):
                        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                        match=False
                        while(match==False):
                                print("Srolling Site")
                                lastCount = lenOfPage
                                time.sleep(2)
                                lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                                if lastCount==lenOfPage:
                                    match=True
                    # Close the Popup Window
                    elements = browser.find_elements_by_id("expanding_cta_close_button")
                    for e in elements:
                        e.click()
                    time.sleep(3)
                    reviewer_urls = browser.find_elements_by_class_name('fcg')
                    # Collect Names
                    nam=[]
                    zero=[]
                    url=[]
                    star =[]
                    userData.clear()
                    # Create user data format
                    for rev in reviewer_urls:
                        try:
                            # Get product name
                            nam.append((rev.find_element_by_css_selector('span').find_element_by_css_selector('span').text))
                            url.append(username)
                            zero.append(0)
                            # Get rating
                            s = (rev.find_element_by_css_selector('i').find_element_by_css_selector('u').text)
                            s = s.replace('star','')
                            s = s.strip()
                            star.append(s)
                            userData.append({
                                    'ID': url,
                                    'name':(rev.find_element_by_css_selector('span').find_element_by_css_selector('span').text),
                                    'star':s,
                                    'Status':0,
                                })
                        except:
                            pass
                    # Get reviews
                    comment = browser.find_elements_by_css_selector("p")
                    num_pages_items = len(comment)
                    c=[]
                    for i in range(num_pages_items):
                        c.append(comment[i].text)
                    processed_features = []
                    features = c
                    # Clean sentences
                    for sentence in range(len(features)):
                    # Remove all the special characters
                        processed_feature = re.sub(r'\W', ' ', str(features[sentence]))
                        # remove all single characters
                        processed_feature= re.sub(r'\s+[a-zA-Z]\s+', ' ', processed_feature)
                        # Remove single characters from the start
                        processed_feature = re.sub(r'\^[a-zA-Z]\s+', ' ', processed_feature)
                        # Substituting multiple spaces with single space
                        processed_feature = re.sub(r'\s+', ' ', processed_feature, flags=re.I)
                        # Converting to Lowercase
                        processed_feature = processed_feature.lower()
                        processed_features.append(processed_feature)
                    # Get date of reviews
                    date = browser.find_elements_by_class_name("_5ptz")
                    num_page_item = len(date)
                    e=[]
                    for i in range(num_page_item):
                        e.append(date[i].get_attribute("title"))
                    dd=[]
                    for elem in e:
                        dd.append(elem[0:10])
                    starname=zip(url,nam,star,processed_features,dd,zero)
                    starname = list(set([s for s in starname]))
                    userDataFrame = pd.DataFrame(starname, columns=['ID','name', 'star','Comment-box','Date','Status'])
                    userDataFrame.to_csv(config['user_db_fb'], index= False, mode ='a', header = None)
                except:
                    userID.clear()
                    userID.append("No Reviews On This Page")
                browser.close()
                xvfb.stop()
            except OSError:
                print(
                    'Error: xvfb cannot be found on your system, please install '
                    'it and try again')
                exit(1)
