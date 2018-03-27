from pandas import DataFrame
import twitter
from string import punctuation
import numpy as np

# Gather lexicon data files
p_words = open('./Lexicons/positive-words.txt','r')
n_words = open('./Lexicons/negative-words.txt','r')

pos_words = [line.rstrip('\n') for line in p_words]
neg_words = [line.rstrip('\n') for line in n_words]

# Remove apostrophe from lexicon since punctuation is stripped later
pos_words = [term.replace("'","") for term in pos_words]
neg_words = [term.replace("'","") for term in neg_words]

# Use developer credentials to connect to Twitter API
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""

auth =  twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth)

# Establish the hashtag to look for and number of tweets to pull
q = '#obamacare'
count = 100
search_results = twitter_api.search.tweets(q = q, count = count)

# Obtain tweet data from JSON file
statuses = search_results['statuses']

# repeat tweet pull -- choose number of attempts by changing range value
for _ in range(1):
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e:
        break
    
    search_results = twitter_api.search.tweets(q=q,count=count)
    statuses += search_results['statuses']
    
# Convert tweet information to DataFrame -- more accessible than JSON
data = DataFrame(statuses)
text_data = data['text']

# make tweets all lower case
text_lower = text_data.str.lower()

# Strip punctuation, newline character from tweets
for i in range(len(text_lower)):
    for p in list(punctuation):
        text_lower[i] = text_lower[i].replace(p,"")
        text_lower[i] = text_lower[i].replace('\n',"")

# Remove retweets to reduce duplicates
for i in range(len(text_lower)):
    if text_lower[i][0:2] == 'rt':
        text_lower = text_lower.drop(i)

# Convert processed tweets to list
final_text = text_lower.values.tolist()
pos_val = []
neg_val = []

# classify words as positive or negative (neutral if not in list)
for i in range(len(text_lower)):
    pos_counter = 0
    neg_counter = 0
    words = final_text[i].encode('ascii','ignore').split() #remove ascii
    for word in words:
        if word in pos_words:
            pos_counter += 1
        if word in neg_words:
            neg_counter += 1
    pos_val.append(pos_counter)
    neg_val.append(neg_counter)

# Number of positive and negative words in each tweet
pos_lex = np.array(pos_val)
neg_lex = np.array(neg_val)

data['pos_words'] = pos_lex
data['neg_words'] = neg_lex
# Calculate sentiment value: positive value indicates positive sentiment
data['sentiment'] = pos_lex-neg_lex
