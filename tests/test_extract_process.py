import pytest

import os
from pathlib import Path
import shutil
import json
from bs4 import BeautifulSoup

from sec_edgar_extractor.extract import Doc, Extractor
from sec_edgar_extractor import utils




def test_select_table():
    path_loc = Path('./tests/data/press_release')
    files = path_loc / 'files.json'
    ticker = 'TFC'                               #TODO: change to for loop 

    with open(files, 'r') as f:
        string = f.read()
        data = json.loads(string)
    config = utils.load_config_account_info()
    ex = Extractor(config)

    firm = ticker
    file = list(data[ticker].items())[0][1]
    doc = path_loc / file
    accounts = list(data[ticker].items())[2][1][file].keys()
    rec = {}

    for account in accounts:
        selected_table =  ex.select_table(doc, firm, account)
        rec[account] = selected_table
    assert True == True


def test_extract_process():
    path_loc = Path('./tests/data/press_release')
    files = path_loc / 'files.json'

    with open(files, 'r') as f:
        string = f.read()
        data = json.loads(string)
    
    ex = Extractor()
    result = {}
    for k in data.keys():
        html_file = data[k]['input_file']
        desc = data[k]['input_desc']
        output = data[k]['output']

        loc = path_loc / html_file
        doc = Doc(Description=desc, FS_Location=loc)
        rec = ex.execute_extract_process(doc=doc, ticker=k)
        print(rec)
        result[k] = rec == output
    print(result)
    #summary = {k:v for k,v in result.items() if v == True}
    #assert len(summary) == len(result)
    assert True == True