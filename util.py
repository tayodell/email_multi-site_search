import os
import random
import requests
import urllib3
import pandas as pd
from pprint import pprint

import constants


user_agent_strings = []


def get_proxies() -> list:
    proxies = []
    with open(os.path.join('data', 'proxies.txt'), 'r') as f:
        for line in f.readlines():
            line = line.strip()
            proxies.append(line)

    return proxies


def get_request(url: str, proxy: bool = True, retry: int = 0, input_headers: dict = None, params: dict = None):
    response = None
    if retry > 9:
        return response
    proxy_list = get_proxies()
    proxy_ip = random.choice(proxy_list)
    if proxy:
        # proxies = {'http': 'http://' + proxy_ip, 'https': 'https://' + proxy_ip}
        proxies = {'http': proxy_ip, 'https': proxy_ip}
        print("Attempting with proxy:", proxy_ip, "try # ", retry)
    try:
        if input_headers and params and proxy:
            response = requests.get(url, proxies=proxies, headers=input_headers, params=params, timeout=3)
        elif input_headers and params:
            response = requests.get(url, headers=input_headers, params=params, timeout=3)
        elif input_headers and proxy:
            response = requests.get(url, proxies=proxies, headers=input_headers, timeout=3)
        elif params and proxy:
            response = requests.get(url, proxies=proxies, params=params, timeout=3)
        elif input_headers:
            response = requests.get(url, headers=input_headers, timeout=3)
        elif params:
            response = requests.get(url, params=params, timeout=3)
        elif proxy:
            response = requests.get(url, proxies=proxies, timeout=3)
        else:
            response = requests.get(url, timeout=3)
        response.raise_for_status()

    # catch HTTP status code error first
    except requests.exceptions.HTTPError as err:
        print('\tHTTPError:', str(response.status_code) + ',', 'retrying...')
        response = get_request(url, retry=retry + 1)
    except requests.exceptions.ProxyError:
        print('\tProxyError, retrying...')
        response = get_request(url, retry=retry + 1)
    except requests.exceptions.SSLError:
        print('\tSSLError, retrying...')
        response = get_request(url, retry=retry + 1)
    except requests.exceptions.Timeout:
        print('\tTimeoutError: retrying...')
        response = get_request(url, retry=retry + 1)

    # watch out for other exceptions
    except requests.exceptions.TooManyRedirects as err:
        print('TooManyRedirects:', str(err))
    except urllib3.exceptions.MaxRetryError as err:
        print('MaxRetryError:', str(err))
    except urllib3.exceptions.NewConnectionError as err:
        print('NewConnectionError:', str(err))
    except urllib3.exceptions.ProtocolError as err:
        print('ProtocolError:', str(err))

    # catch-all exceptions for any other requests/urllib3 errors
    except requests.exceptions.RequestException as err:
        print('Other Requests Exception:', str(err))
    except urllib3.exceptions.RequestError as err:
        print('Other urllib3 Exception:', str(err))

    # generic catch statements to hopefully grab anything else
    except ConnectionError as err:
        print('ConnectionError:', str(err))
    except TimeoutError as err:
        print('Generic TimeoutError:', str(err))
    except OSError as err:
        print('OSError:', str(err))
    except Exception as err:
        print('Other Exception:', str(err))

    return response


def make_api_calls(url, username_key, uuid_key, parser):

    input_data = pd.read_csv(constants.DATA_IN_LOCATION)

    data = {}

    for row in input_data.itertuples():
        email = row[3]
        # username = row[4]

        print(email, '--------------------')
        print(url + email)

        response = get_request(url + email)

        login, uuid = parser(response)

        print('Login:', login)
        print('ID:', uuid)
        data[email] = {username_key: login, uuid_key: uuid}
        print('')

    # print('\nOutput:')
    # pprint(data)

    return data


def github_api_parse(response):

    if response is None:
        return 'Not Found', 'Not Found'
    # print(response.status_code)
    if response.status_code == 200:
        # print(response.text)
        # pprint(response.json()
        if len(response.json().get('items')) == 0:
            return 'Not Found', 'Not Found'
        else:
            try:
                top_result = response.json().get('items')[0]
                return top_result.get('login', 'NULL'), top_result.get('id', 'NULL')
            except IndexError:
                return 'Not Found', 'Not Found'
    else:
        return response.status_code, response.status_code


def custom_dict_print(dictionary: dict, username_key: str, uuid_key: str):

    longest_key = max(dictionary, key=lambda x: len(x))

    usernames = [dictionary[k].get(username_key) for k in dictionary]
    uuids = [dictionary[k].get(uuid_key) for k in dictionary]

    longest_uname = max(usernames, key=lambda x: len(str(x)))
    longest_uuid = max(uuids, key=lambda x: len(str(x)))

    key_pad = len(longest_key) + 5
    uname_pad = len(longest_uname) + 3
    uuid_pad = len(longest_uuid) + 2

    print('Results:')
    header_str = '{e:{kpad}} {n:{npad}} {u:{upad}}'.format(e='email', kpad=key_pad, n=username_key, npad=uname_pad,
                                                           u=uuid_key, upad=uuid_pad)
    print(header_str)
    print('-' * len(header_str))

    for k in dictionary:
        print('{e:{kpad}} {n:{npad}} {u:{upad}}'.format(e=k, kpad=key_pad, n=str(dictionary[k].get(username_key)),
                                                        npad=uname_pad, u=str(dictionary[k].get(uuid_key)),
                                                        upad=uuid_pad))




