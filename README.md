# Find-Tweets-By-Keyword

### \#1 - setup

Next, we install the Pip manager for Python libraries and add the [`Twint`](https://github.com/twintproject/twint) library
```bash
pip install twint
```

To get started, feel free to clone or fork this repo: 
```bash
git clone git@github.com:alecbw/Find-Tweets-By-Keyword.git && cd Find-Tweets-By-Keyword
```

### \#2 - usage

python3 get_tweets_by_keyword.py -o "Tweets about ecom 6.29.csv" -k  "software stack" "stackshare" -l 10

A series of optional command line arguments are provided (only `-k` is required). A list of the full `twint` supported args in at the bottom of `get_tweets_by_keyword.py`:

| CLI Arg                   | Description                                                                           
|---------------------------|-------------------------------------------------------------------------------------------
| '-k', '--keywords'        | A list of keywords (separated by spaces) that you want to search for', required=True
| '-o', '--output_filename' | Set then output filename to something other than the default                             
| '-s', '--since'           | Filter by posted date since a given date. Format is 2019-12-20 20:30:15
| '-u', '--until'           | Filter by posted date until a given date. Format is 2019-12-20 20:30:15
| '-l', '--limit'           | Limit the results per keyword provided                          
| '-m', '--min_likes'       | Limit the results to only tweets with a given number of likes       
| '-n', '--near'            | Limit the results to tweets geolocated near a given city            
| '-v', '--verified'        | Limit the results to tweets made by accounts that are verified       
