import pytest

import os
import time
from pathlib import Path
import shutil
import json
import pandas as pd
from bs4 import BeautifulSoup

from sec_edgar_extractor.extract import Doc, Extractor
from sec_edgar_extractor import utils

'''
TODO:improve press_release_index.json data structure

{
    "C": {
        "c-20211231xex99d2.htm":{
        "input_desc": "EX-99.2",
        "output": {"ACL": XXXX, "PCL": XXXX, "Loans": XXXX, "ACLpctLoan": XXXX}
        },
        "c-20211231xex99d1.htm":{
        "input_desc": "EX-99.1",
        "output": {"ACL": XXXX, "PCL": XXXX, "Loans": XXXX, "ACLpctLoan": XXXX}
        },
    },
    "ALLY": { ...
'''







#records
path_loc = Path('./tests/data/press_release')
files = path_loc / 'press_release_index.json'

with open(files, 'r') as f:
    string = f.read()
    index = json.loads(string)
ex = Extractor()
config = ex.config.get()

recs = []
tickers = list(index.keys())
for ticker in tickers:
    file = list(index[ticker].items())[0][1]
    doc = path_loc / file
    accounts = ['ACL', 'Loans']    

    for account in accounts:
        if (account in list(index[ticker].items())[2][1][file].keys() and 
          account in list(config[ticker].accounts.keys())):
          index[ticker]['input_file']
          recs.append( (ticker, account) )


@pytest.mark.parametrize("ticker, account", recs )
def test_select_table(ticker, account):
    file = list(index[ticker].items())[0][1]
    doc = path_loc / file
    selected_table =  ex.select_table(doc, ticker, account)
    result = True if len(selected_table) > 1000 else False
    assert result == True


@pytest.mark.parametrize("ticker, account", recs )
def test_extract_process(ticker, account):
    """
    All of the tests will run even if one of them fails
    """
    html_file = index[ticker]['input_file']
    desc = index[ticker]['input_desc']
    account_value = index[ticker]['output'][html_file][account]
    loc = path_loc / html_file

    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=ticker)
    val = rec[html_file][account]
    assert val == account_value


def test_extract_process_no_config_data():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'AXP'
    html_file = 'no_file_here.htm'
    desc = 'EX-99 nothing'
    output = {html_file: {}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert rec[html_file] == output[html_file]