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
git clone git@github.com:alecbw/Find-Tweets-By-Keyword.git && cd Find-Tweets-By-Keyword
```

### \#2 - usage

An example invocation is as follows. For phrases with a space, be sure to wrap in double quotation marks
```bash
python3 get_tweets_by_keyword.py -o "Tweets about eCom.csv" -k  "problem with magento" "shopify bug" woocommerce -l 10
```

A series of optional command line arguments are provided (only `-k`/`--keywords` is required):

| CLI Arg                   | Description                                                                           
|---------------------------|-------------------------------------------------------------------------------------------
| '-k', '--keywords'        | A list of keywords (separated by spaces) that you want to search for; required=True
| '-o', '--output_filename' | Set the output filename to something other than the default                             
| '-s', '--since'           | Filter by posted date since a given date. Format is 2019-12-20 20:30:15
| '-u', '--until'           | Filter by posted date until a given date. Format is 2019-12-20 20:30:15
| '-l', '--limit'           | Limit the results per keyword provided                          
| '-m', '--min_likes'       | Limit the results to only tweets with a given number of likes       
| '-n', '--near'            | Limit the results to tweets geolocated near a given city            
| '-v', '--verified'        | Limit the results to tweets made by accounts that are verified     
| '-h', '--hide_output'     | If you want to disable routine results logging;  default=True
| '-r', '--resume'          | Have the search resume at a specific Tweet ID

A list of the full `twint` supported args in at the bottom of `get_tweets_by_keyword.py`
