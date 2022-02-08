import tweepy
import string
from textblob import TextBlob
import pickle
import xlsxwriter
import pandas as pd
import random

###initialising pickle
##tweet_store = {}
##pickle_out = open("unsent.pickle","wb")
##pickle.dump(tweet_store, pickle_out)
##pickle_out.close()
    


# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

me = "Startupedia_HQ"
desired_words = ['startup','start-up','startups','business','bussinesses','company','companies','idea','launch','audience','build','building','fund','funding','leader','leadership','founder','founders','resource','resources','market','marketing','mvp','product','products','entrepreneur','entrepreneurship','profit','sale','sales','social media','job','jobs','problem','problems','wealth','distribution','value','revenue','rich','economy','capital','money']

#Autolike + follow all mentions
##tweets = api.mentions_timeline()
##for tweet in tweets:
##    tweet.favorite()
##    tweet.user.follow()

def tweetPrint():
    for friend in tweepy.Cursor(api.friends, id=me).items(100):
        statuses = api.user_timeline(friend.id,count = 5)
        print(friend.screen_name)
        for status in statuses:
            tweet = api.get_status(status.id, tweet_mode="extended")
            if status.in_reply_to_status_id is not None or \
                status.user.id == me:
                continue
            else:
                tweettext = tweet.full_text
                if (tweettext.startswith("rt") or tweettext.startswith("RT")):
                    continue
                if (text_processor(tweettext)):
                    if (fetch_tweet_from_repo(status.id)):
                        continue
                    else:
                        add_tweet_to_repo(status.id,tweettext)
                        print(final_tweet)         #to see what's being tweeted
            print("************************* next tweet **************************")
            
def text_processor(tweettext):
    cleaned_text = clean_text(tweettext)
    wiki = TextBlob(cleaned_text)
    wiki = wiki.correct()
    word_list = [word.lemmatize() for word in wiki.words]
    for i in word_list:
        if i in desired_words:
            return True
##            print(i)                  #to know which word of tweet matched with desired words
    return False
    
def clean_text(text):
    text = text.lower()
    return ''.join(i for i in text if i in (string.ascii_letters) or (i==' '))

def add_tweet_to_repo(key,value):   
    pickle_in = open("dict.pickle","rb")
    tweetstorage = pickle.load(pickle_in)
    pickle_in2 = open("unsent.pickle","rb")
    tweetstorage2 = pickle.load(pickle_in2)
    if(key not in tweetstorage):
        temp = {key:value}
        tweetstorage.update(temp)
        tweetstorage2.update(temp)
        pickle_in.close()
        pickle_in2.close()
        pickle_out = open("dict.pickle","wb")
        pickle.dump(tweetstorage, pickle_out)
        pickle_out.close()
        pickle_out2 = open("unsent.pickle","wb")
        pickle.dump(tweetstorage2, pickle_out2)
        pickle_out2.close()
        xlsx_repo()
        return True
    else:
        return False

def fetch_tweet_from_repo(key):
    pickle_in = open("dict.pickle","rb")
    tweetstorage = pickle.load(pickle_in)
    try:
        print(tweetstorage[key])
        pickle_in.close()
        return True
    except KeyError:
        pickle_in.close()
        print("Tweet not present in Repo")
        return False

def xlsx_repo():    
    pickle_in = open("dict.pickle","rb")
    tweetstorage = pickle.load(pickle_in)
    tweetstorage = list(tweetstorage.items())
    tweetstorage = [[str(i),j] for i,j in tweetstorage]
    tweetstorage = pd.DataFrame(tweetstorage)
##    print(tweetstorage)
    writer = pd.ExcelWriter('tweetdata.xlsx', engine='xlsxwriter', options={'strings_to_numbers': False})
    tweetstorage.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    pickle_in.close()
    return

def scheduler():
    pickle_in = open("unsent.pickle","rb")
    tweetstorage = pickle.load(pickle_in)
    random_key = random.choice(list(tweetstorage.keys()))
    tweetMaker(random_key)
    del tweetstorage[random_key]
    pickle_in.close()
    pickle_out = open("unsent.pickle","wb")
    pickle.dump(tweetstorage, pickle_out)
    pickle_out.close()
    return
    
def tweetMaker(key):
    # Authenticate to Twitter
    # add your credentials here
    auth = tweepy.OAuthHandler("**********************", "**************************************************")  #consumer key, consumer secret
    auth.set_access_token("*************-****************", "***********")                                      #access token, access token secret
    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

    tweet = api.get_status(key, tweet_mode="extended")
    final_tweet = tweet.full_text+"\n ~@"+tweet.user.screen_name
    print(final_tweet)
    if (len(final_tweet)<=280):
        api.update_status(final_tweet)
        print(final_tweet)
    else:
        if not (tweet.retweeted):
            tweet.retweet(key)
    return


##scheduler()

###dictionary of all the tweets so far
##pickle_in = open("dict.pickle","rb")
##tweetstorage = pickle.load(pickle_in)
##print(len(tweetstorage))

##tweetPrint()

##xlsx_repo()
