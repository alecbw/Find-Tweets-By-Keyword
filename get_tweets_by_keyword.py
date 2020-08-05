from time import sleep
from datetime import datetime, timedelta
import csv
import os
import argparse
import logging

logging.getLogger().setLevel(logging.INFO)

try:
    import twint
    import gspread
    from google.oauth2.service_account import Credentials
    from google.oauth2 import service_account
except ImportError:
    sys.exit("~ Make sure you install twint. Run `pip install twint google-auth gspread` and try this again ~")


argparser = argparse.ArgumentParser()
argparser.add_argument('-k', '--keywords', nargs='+', help='<Required> A list of keywords (separated by spaces) that you want to search for', required=True)
argparser.add_argument('-o', '--output_filename', nargs='?', default="! Resulting Tweets.csv", help="If you want an output filename other than the default")
argparser.add_argument('-g', '--output_gsheet', nargs='?', help="Write to Google Sheets with the spreadsheet name you specify")
argparser.add_argument('-d', '--deduplicate', nargs='?', default="! Resulting Tweets.csv", help="If you want an output filename other than the default")
argparser.add_argument('-s', '--since', nargs='?', default=None, help="If you want to filter by posted date since a given date. Format is 2019-12-20 20:30:15")
argparser.add_argument('-u', '--until', nargs='?', default=None, help="If you want to filter by posted date until a given date. Format is 2019-12-20 20:30:15")
argparser.add_argument('-l', '--limit', nargs='?', default=None, help="If you want to limit the results per keyword provided")
argparser.add_argument('-m', '--min_likes', nargs='?', default=None, help="If you want to limit the results to only tweets with a given number of likes")
argparser.add_argument('-n', '--near', nargs='?', default=None, help="If you want to limit the results to tweets geolocated near a given city")
argparser.add_argument('-v', '--verified', nargs='?', default=None, help="If you want to limit the results to tweets made by accounts that are verified")
argparser.add_argument('-q', '--hide_output', nargs='?', default=True, help="If you want to disable routing results logging")
argparser.add_argument('-r', '--resume', nargs='?', default=None, help="Have the search resume at a specific Tweet ID")

args = argparser.parse_args()
args = vars(args) # convert to dict


######################## GSheets Helpers #########################################

def auth_gspread():
    auth = {
        "private_key": os.environ["GSHEETS_PRIVATE_KEY"].replace("\\n", "\n").replace('"', ''),
        "client_email": os.environ["GSHEETS_CLIENT_EMAIL"],
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    scopes = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(auth, scopes=scopes)
    gc = gspread.authorize(credentials)
    return gc


def write_new_google_sheet(result_lod, output_filename):
    sh = gc.open(output_filename)
    tab = sh.get_worksheet(0)  # get the first tab

    tab.update([list(result_lod[0].keys())] + [list(x.values()) for x in result_lod])

    tab.resize(
        rows=len(result_lod),
        cols=len(result_lod[0])
    )
    logging.info(f"Successful write to Google Sheet {output_filename}")
    

###############################################################################


def deduplicate_lod(input_lod, primary_key):
    if not primary_key:
        output_lod = {json.dumps(d, sort_keys=True) for d in input_lod}  # convert to JSON to make dicts hashable
        return [json.loads(x) for x in output_lod]                 # unpack the JSON

    output_dict = {}
    for d in input_lod:
        if d.get(primary_key) not in output_dict.keys():
            output_dict[d[primary_key]] = d

    return list(output_dict.values())
    

def unpack_twint_tweet(keyword, tweet_list):

    output_lod = []

    for n, tweet in enumerate(tweet_list):
        output_dict = {
            'tweet_id': tweet.id,
            'keyword_searched': keyword,
            'author_account': tweet.username,
            'author_name': tweet.name,
            'author_id': tweet.user_id,
            'created_at': datetime.strftime(datetime.fromtimestamp(tweet.datetime/1000), '%Y-%m-%d %H:%M:%S'),
            'timezone': tweet.timezone,
            'geo': tweet.place or tweet.near, # geo may not be working TODO
            'text': tweet.tweet,
            'link': tweet.link,
            'urls': ", ".join(tweet.urls),
            'mentions': ", ".join(tweet.mentions),
            'likes': tweet.likes_count,
            'retweets': tweet.retweets_count,
            'replies': tweet.replies_count,
            'in_reply_to_screen_name': ", ".join([x.get('username') for x in tweet.reply_to]) if tweet.reply_to else None,
            'QT_url': tweet.quote_url,
            # 'RT': tweet.retweet,f
            # 'user_rt': tweet.user_rt,
            # 'user_rt_id': tweet.user_rt_id,
            # 'rt_id': tweet.retweet_id,
            # 'user_rt_date': tweet.retweet_date,
        }
        output_lod.append(output_dict)

    return output_lod


def twint_scrape(keyword, args):
    c = twint.Config()
    c.Search = keyword

    for k,v in args.items():
        if isinstance(v, str) and v.title() == "False":  # argparse converts to str
            setattr(c, k.capitalize(), False)
        elif v:
            setattr(c, k.capitalize(), v)

    tweets = []
    c.Store_object = True  # preferable to using twint.output.tweets_list
    c.Store_object_tweets_list = tweets

    # c.Resume = "scrape_interrupted_last_id.csv" # TODO implement save-last-scroll-id
    twint.run.Search(c)


    output_lod = unpack_twint_tweet(keyword, tweets) 

    logging.info(f"The keyword {keyword} has produced {len(output_lod)} tweets")
    return output_lod


if __name__ == "__main__":
    result_lod = []
    deduplicate_option = args.pop("deduplicate")

    if args.get("output_gsheet", False):
        output_filename = args.pop("output_gsheet")
        gc = auth_gspread()
    else:
        output_filename = args.pop("output_filename") + ".csv" if ".csv" not in args.get("output_filename") else args.pop("output_filename")

    for keyword in args.pop("keywords"):
        logging.info(f"Now processing keyword {keyword}")
        result_lod += twint_scrape(keyword, args)

    if deduplicate_option:
        logging.info("Deduplicating")
        result_lod = deduplicate_lod(result_lod, 'tweet_id')

    if ".csv" in output_filename:
        logging.info(f"Now writing to file: {output_filename}")
        with open(output_filename, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, result_lod[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(result_lod)
    else:
        write_new_google_sheet(result_lod, output_filename)

    # os.remove("scrape_interrupted_last_id.csv")

#########################################################################################################

"""
all twint optional arguments:
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

# def show_tweet(link):
#     '''Display the contents of a tweet. '''
#     url = 'https://publish.twitter.com/oembed?url=%s' % link
#     response = requests.get(url)
#     html = response.json()["html"]
#     display(HTML(html))/publish.twitter.com/oembed?url=%s' % link