from flask import Flask
from flask_restful import Resource, Api
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

app = Flask(__name__)
api = Api(app)

class TwitterClient(Resource):
	'''
	Generic Twitter Class for sentiment analysis.
	'''
	# def get(self,query):
    #     return query
	def __init__(self):
		'''
		Class constructor or initialization method.
		'''
		# keys and tokens from the Twitter Dev Console
		consumer_key = 'rjJMKOpi8y0XnEXvXC1cuFo9A'
		consumer_secret = 'A8xOjrtI17TTLGLl7bWnUSNMeIv3w5SPm6pUnV3Dwr8MPgPzFx'
		access_token = '1379755625039622144-whGwS56ICHzXptsTsReFhxBWP8HkiE'
		access_token_secret = 'mxLrqfGrm59iDHmRD0InVFmLf0x3BtrcD4fsmFfDVtN44'

		# attempt authentication
		try:
			# create OAuthHandler object
			self.auth = OAuthHandler(consumer_key, consumer_secret)
			# set access token and secret
			self.auth.set_access_token(access_token, access_token_secret)
			# create tweepy API object to fetch tweets
			self.api = tweepy.API(self.auth)
		except:
			print("Error: Authentication Failed")

	def clean_tweet(self, tweet):
		'''
		Utility function to clean tweet text by removing links, special characters
		using simple regex statements.
		'''
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

	def get_tweet_sentiment(self, tweet):
		'''
		Utility function to classify sentiment of passed tweet
		using textblob's sentiment method
		'''
		# create TextBlob object of passed tweet text
		analysis = TextBlob(self.clean_tweet(tweet))
		# set sentiment
		if analysis.sentiment.polarity > 0:
			return 'positive'
		elif analysis.sentiment.polarity == 0:
			return 'neutral'
		else:
			return 'negative'    
	def get(self, query, count = 10):
		'''
		Main function to fetch tweets and parse them.
		'''
		# empty list to store parsed tweets
		tweets = []

		try:
			# call twitter api to fetch tweets
			fetched_tweets = self.api.search(q = query, count = count)

			# parsing tweets one by one
			for tweet in fetched_tweets:
				# empty dictionary to store required params of a tweet
				parsed_tweet = {}

				# saving text of tweet
				parsed_tweet['text'] = tweet.text
				# saving sentiment of tweet
				parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

				# appending parsed tweet to tweets list
				if tweet.retweet_count > 0:
					# if tweet has retweets, ensure that it is appended only once
					if parsed_tweet not in tweets:
						tweets.append(parsed_tweet)
				else:
					tweets.append(parsed_tweet)

			# return parsed tweets
			ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
			ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
			return {"ptweets":format(100*len(ptweets)/len(tweets)),
			        "ntweets":format(100*len(ntweets)/len(tweets)),
					"neutraltweet":format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets)),
				    "10ptweets":ptweets[:10],
					"10ntweets":ntweets[:10]
				   }

		except tweepy.TweepError as e:
			# print error (if any)
			print("Error : " + str(e))
    


api.add_resource(TwitterClient, '/<string:query>')

if __name__ == '__main__':
    app.run(debug=True)