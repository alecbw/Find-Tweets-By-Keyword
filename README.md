# Find-Tweets-By-Keyword

[`Twint`](https://github.com/twintproject/twint) is an amazing library for scraping Twitter without worrying about Twitter auth or rate limits. It has a comprehensive CLI interface that I encourage you to go use if you want to explore your own specific use cases.

This library in particular covers scraping for multiple keywords at once.

### \#1 - setup

First, we add the [`Twint`](https://github.com/twintproject/twint) library
```bash
pip install twint
```

To get started, feel free to clone or fork this repo: 
```bash
git clone  git://github.com/alecbw/Find-Tweets-By-Keyword.git && cd Find-Tweets-By-Keyword
```

### \#2 - usage

An example invocation is as follows. For phrases with a space, be sure to wrap in double quotation marks
```bash
python3 get_tweets_by_keyword.py -o "Tweets about eCom.csv" -k  "problem with magento" "shopify bug" woocommerce -l 10
```

A series of optional command line arguments are provided (only `-k`/`--keywords` is required):

| Option                   | Description                                                                           
|---------------------------|-------------------------------------------------------------------------------------------
| '-k' or '--keywords'        | A list of keywords (separated by spaces) that you want to search for; required=True
| '-o' or '--output_filename' | Set the output filename to something other than the default                             
| '-g' or '--output_gsheet' | Write to Google Sheets with the spreadsheet name you specify
| '-s' or '--since'           | Filter by posted date since a given date. Format is 2019-12-20 20:30:15
| '-u' or '--until'           | Filter by posted date until a given date. Format is 2019-12-20 20:30:15
| '-l' or '--limit'           | Limit the results per keyword provided                          
| '-m' or '--min_likes'       | Limit the results to only tweets with a given number of likes       
| '-n' or '--near'            | Limit the results to tweets geolocated near a given city            
| '-v' or '--verified'        | Limit the results to tweets made by accounts that are verified     
| '-q' or '--hide_output'     | If you want to disable routine results logging;  default=True
| '-r' or '--resume'          | Have the search resume at a specific Tweet ID


A list of the full `twint` supported args in at the bottom of `get_tweets_by_keyword.py`


### \#3 - GSheets Writes

If you've read my [Google Sheets API walkthrough](https://www.alec.fyi/set-up-google-sheets-apis-and-treat-sheets-like-a-database.html), you can easily write to Google Sheets. If you haven't, go set up the auth, as described there. 

The beauty of the Google Sheets write is you can have one person responsible for running the script (or put it on a cronjob!) and have it write to a Sheet that is shared with others (e.g. a whole marketing team)

When setting up the Sheet, remember you need to share the Sheet with your `gserviceaccount`. You'll also need to `export` the `GSHEETS_PRIVATE_KEY` and `GSHEETS_CLIENT_EMAIL` to the local environment. Each write will overwrite the first tab.

### \#4 - performance

In the (admittedly small) amount of testing I've done, the script can generate 1500-2000 tweets/minute. If you intend to scale this to a significant volume, I advise that you distribute your workers across multiple boxes & IP's.
