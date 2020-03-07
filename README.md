# Reviewer Verificiation System 
#live demo www.isreviewfake.com
# About 
People review restaurants, contractors, sites.. almost everything. Reviews make great impact in decision making process. Some people take advantage of it by posting fake, fabricated reviews to upvote or downvote a particular target. We are trying to approach this problem by classifiying such reviews.
# Project 
By using Vader Sentiment Analysis and Jacccard Similarity, a reviewer verification system is created to allocate probabilites of a reviewer being authentic,fake, or a bot. For an instance, if probability of a reviewer being fake is above 0.90, it can be safe to assume and avoid such reviewes from these reviewers. For this project, we dig-in amazon (www.amazon.com), yelp (www.yelp.com), facebook and google to apply our 'intelligent system' to classify reviews.
# Tech 
+ Python 3 
+ NLTK 
+ Numpy 
+ Pandas 
+ Beautifulsoup4 
+ Requests 
+ Vader Sentiment Analysis 
+ Django 2
+ Regular Expression 
# How to Run Program {BETA}
### Online ###
- Visit "isreviewfake.com".
- In the input form, type in User ID, or the URL that links to User Profile.
- Click Verify*.
* Loading time depends on processing. Please give it few seconds.
### Offline ###
- `git clone {project url}`
- Install all the dependencies mentioned above from requirements.txt using `pip install -r requirements.txt`.
- Go to the project folder, and in the directory that has "manage" python file, create a JSON file.
- Open Terminal in the folder directory. 
- `python3 manage.py runserver [your IP address]:[port number]`
- Open the link given in the terminal.
# FORMAT OF 'config.json' file:
{
  "ENV": "development" FOR DEV PURPOSE, or "production" FOR PROD PURPOSE
  "SECRET_KEY" : YOUR DJNAGO SECRET KEY,
  "NLTK_PATH": YOUR PATH TO NLTK DATA,
  "ALLOWED_HOSTS": ["localhost","127.0.0.1"] ADD MORE IF NEEDED,
  "user_db_yelp": CSV PATH FOR YELP,
  "user_db_am": CSV PATH FOR AMAZON,
  "user_db_fb": CSV PATH FOR FACEBOOK,
  "user_db_google": CSV PATH FOR GOOGLE,
  "chdir_org":PATH TO BASE DIR,
  "chdir_scrapper":PATH TO SCRAPY DIR,
  "chromedriver":PATH TO CHROME DRIVER,
  "proxy_dir":PATH TO PROXY,
  "log_dir":PATH TO LOG"
}

# IMPORTANT: PLEASE USE VPN TO AVOID GETTING YOUR IP BLOCKED BY SITE.
# fake_product_review_check
Detect review manipulation by leveraging reviewer historical stylometrics in Amazon, Yelp, Facebook and Google reviews

Consumers now check reviews and recommendations before consuming any services or products. But traders try to shape reviews and ratings of their merchandise to gain more consumers. Seldom they attempt to manage their competitor's review and recommendation.  These manipulations are hard to detect by standard lookup from an everyday consumer, but by thoroughly examining, customers can identify these manipulations. In this paper, we try to mimic how a specialist will look to detect review manipulation and came up with algorithms that are compatible with significant and well known online services. We provide a historical stylometry based methodology to detect review manipulations and supported that with results from Amazon, Yelp, Google, and Facebook.

Developed by:

Nafiz Sadman https://github.com/Nafiz95

Kishor Datta Gupta github.com/kishordgupta/  kdgupta87 @gmail.com

Sajib Sen sajibsen.eee@gmail.com 

Ariful Haque Ariful@siliconorchard.com
