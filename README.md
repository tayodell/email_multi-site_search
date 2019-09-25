# phoenix-01

### Structure:  
`phoenix-gh-join/`  
`|-- README.md`  
`|-- __init__.py`  
`|-- constants.py`  
`|-- util.py`  
`|-- main.py`  
`|-- data/`  
`|   |-- data.csv`  
`|   |-- output.csv`  
`|   |-- proxies.txt`  

* `phoenix-gh-join/` - main project folder
* `README.md` - this very informational document
* `__init__.py` - for project structure - helps with local imports
* `constants.py` - contains location of our input/output file(s)
* `util.py` - functions that get called more than once or perform  a subset of functions
* `main.py` - main program file that handles the heavy lifting
* `data/` - storage folder
* `data/data.csv` - "in" file containing emails/usernames that we're checking for, along with other fields. Can be 
changed by editing the value for `DATA_IN_LOCATION` in `constants.py`
* `data/output.csv` - "out" file that our results are written to. Can be 
changed by editing the value for `DATA_OUT_LOCATION` in `constants.py`. For testing it's easier to have two different
 files so that if something is wrong you're not overwriting your source file every time. Once the kinks are worked 
 out, `DATA_IN_LOCATION` and `DATA_OUT_LOCATION` can be the same file.
* `data/proxies.txt` - list of proxies. Proxies get chosen randomly when making a request

&nbsp;

## How it works
1. In `main.py`, the function `main()` is called when you run `python3 main.py` from the command line while in the 
main project folder, `phoenix-gh-join`.
2. `main()` is responsible for calling other functions/modules that we want to run. Currently, the only module 
implemented is for GitHub, so the only function call in `main()` is to `github_api()`.
3. `github_api()` sets up the constants to pass to `make_api_calls()` in `util.py`. For this function, we're using 
the url `https://api.github.com/search/users?q=` to check and see if emails found in `data.csv` can be 
matched to GitHub accounts. We also set the `username_key` and `uuid_key` to `gh_login` and `gh_uuid`, which become the 
names of the columns in the outputted CSV.
4. `util.make_api_call()` is then called, and it is passed the `url`, `username_key`, `uuid_key`, and the parser that
 we also defined in `util.py`.
5. Now in the `util.py` file, `make_api_call()` does the heavy lifting of making requests. 
    * It reads in the data from 
the file location in `constants.py`, and then it iterates over the dataset to make a request for each email address 
(and sometimes username). Important to note that this depends on the `email` column being at index 3 in the list, so if the source data file is updated to be in a different order, this function will 
need updated as well. 
    * For each row in the dataset, `make_api_call()` will query the given API address, appending the 
email address for that row.
The requests are made by calling the function `get_request()`. 
    * For the purpose of this module, we only need to give `get_request()` a URL and it will handle the rest of the 
    request. It reads in the list of proxies from `data/proxies.txt`. It then chooses a proxy randomly and attempts 
    the request. Upon a ProxyError or SSLError, it will attempt to make the request again with a different proxy, up 
    to 10 times. It will also re-request up to 10 times if it receives a status code other than 200 (to handle those 
    pesky 403 - Too Many Request errors). `get-request()` then returns the response from the `requests` module back 
    to `make_api_call()` for parsing.
    * `make_api_call()` takes a function for it's `parser` argument, so for this example we give it the function 
    `github_api_parse()`. This function takes the response from `get-request()` and returns the username and uuid, if
     it finds any. If none are found, it will return 'Not Found' for both items.
     * `make_api_call()` then takes the values output from `github_api_parse()` (or whatever parser you give as an 
     argument) and stores it in a dictionary with the key being the email address of the row. This dictionary is then
      returned out to the `github_api()` function
6. Back in `main.py`, `github_api()` takes the dictionary it receives and turns it into a Pandas DataFrame object 
with the correct format to easily merge with the DataFrame created from the original CSV that gets read in as well. A
 standard left join() is done to combine these two DataFrames, and then the DataFrame is output to the original file 
 location as specified in `constants.py`. It also uses `custom_dict_print()` from `util.py` to give us a nice pretty 
 output of the results.

&nbsp;


## Adding a new API bot
To add a new bot, you really just need to implement two functions. 
1. Create one function in `main.py` that mimics the 
functionality of `github_api()` and then create another function in `util.py` that mimics the function of 
`github_api_parse()`.
2. In your copy of `github_api()` in `main.py`, most of what you need to do is just change the variable values. 
Specifically, replace the GitHub api url with your new api url for the `api` variable. Set `username_key` and 
`uuid_key` to whatever you want to call your new columns. The only other thing that will be different about this 
function than in `github_api()` is the parser you pass to `make_api_calls()` in this command: 
`output_dict = util.make_api_calls(url, username_key, uuid_key, util.github_api_parse)`. Instead of `util
.github_api_parse`, you'll pass in the name of the parser function you create in the next step. The rest of the code 
copied from `github_api()` can stay the same.
3. In `util.py`, you now need to implement your version of `github_api_parse()`. This is the most code-intensive part
 of adding a new API bot as this is where you'll need to parse out the results of your API (or regular URL) call. If 
 you are making calls to a regular web page, you'll probably need to use a parsing library like BeautifulSoup to 
 extract the elements you need. If using an API that speaks JSON, you can pretty closely mimic the code in 
 `github_api_parse()` and just adjust it to fit the structure of the JSON you're working with. As an example, below 
 is the JSON that is returned from the call to `https://api.github.com/search/users?q=damienradford@gmail.com`:  

   `{`  
  &nbsp;&nbsp;`"total_count": 1,`  
  &nbsp;&nbsp;`"incomplete_results": false,`  
  &nbsp;&nbsp;`"items": [`  
  &nbsp;&nbsp;&nbsp;&nbsp;`{`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "login": "dradford",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "id": 77323,`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "node_id": "MDQ6VXNlcjc3MzIz",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "avatar_url": "https://avatars0.githubusercontent.com/u/77323?v=4",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "gravatar_id": "",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "url": "https://api.github.com/users/dradford",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "html_url": "https://github.com/dradford",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "followers_url": "https://api.github.com/users/dradford/followers",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "following_url": "https://api.github.com/users/dradford/following{/other_user}",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "gists_url": "https://api.github.com/users/dradford/gists{/gist_id}",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "starred_url": "https://api.github.com/users/dradford/starred{/owner}{/repo}",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "subscriptions_url": "https://api.github.com/users/dradford/subscriptions",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "organizations_url": "https://api.github.com/users/dradford/orgs",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "repos_url": "https://api.github.com/users/dradford/repos",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "events_url": "https://api.github.com/users/dradford/events{/privacy}",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "received_events_url": "https://api.github.com/users/dradford/received_events",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "type": "User",`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "site_admin": false,`  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`    "score": 53.497757`  
  &nbsp;&nbsp;&nbsp;&nbsp;`  }`  
  &nbsp;&nbsp;`]`  
`}`

    In the above example, the path the the values that we care about ('login' and 'id') is to grab the first element of 
the list `items` and then we can use `.get()` to query the object for the values we want, and this is what 
`github_api_parse()` is doing. `github_api_parse()` also has some built-in error checking that will return `Not 
Found` in the event that the API request didn't work or if there is no GitHub account found for the email address we 
queried for.
4. Once you have your two functions implemented and tested, adding the function you created in `main.py` to the 
`main()` function will run that function every time the `main.py` file is run.
