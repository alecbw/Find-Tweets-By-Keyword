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
argparser.add_argument('-o', '--output_filename', nargs='?', default="! Resulting Tweets.csv", help="If you want an output filename other than the default")
argparser.add_argument('-s', '--since', nargs='?', default=None, help="If you want to filter by posted date since a given date. Format is 2019-12-20 20:30:15")
argparser.add_argument('-u', '--until', nargs='?', default=None, help="If you want to filter by posted date until a given date. Format is 2019-12-20 20:30:15")
argparser.add_argument('-l', '--limit', nargs='?', default=None, help="If you want to limit the results per keyword provided")
argparser.add_argument('-m', '--min_likes', nargs='?', default=None, help="If you want to limit the results to only tweets with a given number of likes")
argparser.add_argument('-n', '--near', nargs='?', default=None, help="If you want to limit the results to tweets geolocated near a given city")
argparser.add_argument('-v', '--verified', nargs='?', default=None, help="If you want to limit the results to tweets geolocated near a given city")

args = argparser.parse_args()
args = vars(args) # convert to dict


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
    print(args)
    for k,v in args.items():
        if v:
            c.__setattr__(k.title(),v)
    # print(args)
    # if args.l:
    #     c.Limit = args.l
    # if args.s:
    #     c.Since = args.s
    # if args.u:
    #     c.Until = args.u
    # if args.m:
    #     c.Min_likes = args.m
    # if args.n:
    #     c.Near = args.n
    # if args.v:
    #     c.Verified = args.v

    c.Hide_output = True
    c.Store_object = True
    print(vars(c))
    twint.run.Search(c)
    output_lod = unpack_twint_tweet(twint.output.tweets_list)

    print(output_lod)
    return output_lod


if __name__ == "__main__":
    result_lod = []
    output_filename = args.pop("output_filename") + ".csv" if ".csv" not in args.get("output_filename") else args.pop("output_filename")

    for keyword in args.pop("keywords"):
        logging.info(f"Now processing keyword {keyword}")
        result_lod += twint_scrape(keyword, args)

    with open(output_filename, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, result_lod[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(result_lod)


#########################################################################################################

"""
optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        User's Tweets you want to scrape.
  -s SEARCH, --search SEARCH
                        Search for Tweets containing this word or phrase.
  -g GEO, --geo GEO     Search for geocoded Tweets.
  --near NEAR           Near a specified city.
  --location            Show user's location (Experimental).
  -l LANG, --lang LANG  Search for Tweets in a specific language.
  -o OUTPUT, --output OUTPUT
                        Save output to a file.
  -es ELASTICSEARCH, --elasticsearch ELASTICSEARCH
                        Index to Elasticsearch.
  -t TIMEDELTA, --timedelta TIMEDELTA
                        Time interval for every request.
  --year YEAR           Filter Tweets before specified year.
  --since SINCE         Filter Tweets sent since date (Example: 2017-12-27).
  --until UNTIL         Filter Tweets sent until date (Example: 2017-12-27).
  --email               Filter Tweets that might have email addresses
  --phone               Filter Tweets that might have phone numbers
  --verified            Display Tweets only from verified users (Use with -s).
  --csv                 Write as .csv file.
  --json                Write as .json file
  --hashtags            Output hashtags in seperate column.
  --userid USERID       Twitter user id.
  --limit LIMIT         Number of Tweets to pull (Increments of 20).
  --count               Display number of Tweets scraped at the end of
                        session.
  --stats               Show number of replies, retweets, and likes.
  -db DATABASE, --database DATABASE
                        Store Tweets in a sqlite3 database.
  --to TO               Search Tweets to a user.
  --all ALL             Search all Tweets associated with a user.
  --followers           Scrape a person's followers.
  --following           Scrape a person's follows
  --favorites           Scrape Tweets a user has liked.
  --proxy-type PROXY_TYPE
                        Socks5, HTTP, etc.
  --proxy-host PROXY_HOST
                        Proxy hostname or IP.
  --proxy-port PROXY_PORT
                        The port of the proxy server.
  --essid [ESSID]       Elasticsearch Session ID, use this to differentiate
                        scraping sessions.
  --userlist USERLIST   Userlist from list or file.
  --retweets            Include user's Retweets (Warning: limited).
  --format FORMAT       Custom output format (See wiki for details).
  --user-full           Collect all user information (Use with followers or
                        following only).
  --profile-full        Slow, but effective method of collecting a user's
                        Tweets and RT.
  --store-pandas STORE_PANDAS
                        Save Tweets in a DataFrame (Pandas) file.
  --pandas-type [PANDAS_TYPE]
                        Specify HDF5 or Pickle (HDF5 as default)
  --search_name SEARCH_NAME
                        Name for identify the search like -3dprinter stuff-
                        only for mysql
  -it [INDEX_TWEETS], --index-tweets [INDEX_TWEETS]
                        Custom Elasticsearch Index name for Tweets.
  -if [INDEX_FOLLOW], --index-follow [INDEX_FOLLOW]
                        Custom Elasticsearch Index name for Follows.
  -iu [INDEX_USERS], --index-users [INDEX_USERS]
                        Custom Elasticsearch Index name for Users.
  --debug               Store information in debug logs
  --resume RESUME       Resume from Tweet ID.
  --videos              Display only Tweets with videos.
  --images              Display only Tweets with images.
  --media               Display Tweets with only images or videos.
  --replies             Display replies to a subject.
  -pc PANDAS_CLEAN, --pandas-clean PANDAS_CLEAN
                        Automatically clean Pandas dataframe at every scrape.
  --get-replies         All replies to the tweet.
"""