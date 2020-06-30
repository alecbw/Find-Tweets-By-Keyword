from time import sleep
from datetime import datetime, timedelta
import csv
import os
import argparse
import logging
logger = logging.getLogger()

try:
    import twint
except ImportError:
    sys.exit("~ Make sure you install twint. Run `pip install twint` and try this again ~")

argparser = argparse.ArgumentParser()
argparser.add_argument('-k','--keywords', nargs='+', help='<Required> A list of keywords (separated by spaces) that you want to search for', required=True)
argparser.add_argument('-o', '-output_filename', nargs='?', default="! Resulting Tweets.csv", help="If you want an output filename other than the default")
argparser.add_argument('-s', '-since', nargs='?', default=None, help="If you want to filter by posted date since a given date. Format is 2019-12-20 20:30:15")
argparser.add_argument('-u', '-until', nargs='?', default=None, help="If you want to filter by posted date until a given date. Format is 2019-12-20 20:30:15")
argparser.add_argument('-l', '-limit', nargs='?', default=None, help="If you want to limit the results per keyword provided")
args = argparser.parse_args()


###############################################################################

def unpack_twint_tweet(tweet_list):

    output_lod = []
    for n, tweet in enumerate(tweet_list):
        output_dict = {
        'author_account': tweet.username,
        'author_name': tweet.name,
        # 'author_description': tweet.author.description,
        # 'author_location': tweet.author.location,
        'author_url': tweet.user_id,
        'created_at': tweet.timestamp,
        'geo': tweet.geo,
        'id': tweet.id,
        'in_reply_to_screen_name': tweet.reply_to,
        # 'in_reply_to_status_id': tweet.in_reply_to_status_id,
        # 'in_reply_to_user_id': tweet.in_reply_to_user_id,
        'is_quote_status': tweet.quote_url,
        'lang': tweet.translate,
        'retweets': tweet.retweets_count,
        'source': tweet.source,
        'text': tweet.tweet,
        'link': tweet.link,
        'likes': tweet.likes_count,
        'urls': tweet.urls
        }
        # for key in [ 'conversation_id', '', 'datetime', , '','mentions', 'name', 'near', 'photos', 'place', '', 'replies_count', '', '', 'retweet_date', 'retweet_id', 'retweets_count', '', 'timezone', 'trans_dest', 'trans_src', '', 'tweet', 'type', '', '', 'user_id_str', 'user_rt', 'user_rt_id', '', 'video']:
        output_lod.append(output_dict)

    return output_lod

def twint_scrape(keyword, args):
    c = twint.Config()
    c.Search = keyword
    if hasattr(args, 'l'):
        c.Limit = args.limit
    if hasattr(args, 's'):
        c.Since = args.since
    if hasattr(args, 'u'):
        c.Until = args.until

    c.Store_object = True
    twint.run.Search(c)
    output_lod = unpack_twint_tweet(twint.output.tweets_list)

    print(output_lod)
    return output_lod

if __name__ == "__main__":
    result_lod = []
    for keyword in args.keywords:
        result_lod += twint_scrape(keyword, args)

    with open('output.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, result_lod[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(result_lod)