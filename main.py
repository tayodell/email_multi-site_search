import json
import pandas as pd
from pprint import pprint

import util
import constants


def github_api():
    url = "https://api.github.com/search/users?q="

    username_key = 'gh_login'
    uuid_key = 'gh_uuid'

    output_dict = util.make_api_calls(url, username_key, uuid_key, util.github_api_parse)

    data = pd.read_csv(constants.DATA_IN_LOCATION)

    output_df = pd.DataFrame.from_dict(output_dict).T

    data = data.join(output_df, on='email', how='left')

    data.set_index('id', inplace=True)

    data.to_csv(constants.DATA_OUT_LOCATION)

    util.custom_dict_print(output_dict, username_key, uuid_key)

    print('\nFinished. CSV written to:', constants.DATA_OUT_LOCATION)


def main():
    github_api()


if __name__ == '__main__':
    main()
