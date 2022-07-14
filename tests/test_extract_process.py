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







#records
path_loc = Path('./tests/data/press_release')
files = path_loc / 'press_release_index.json'

with open(files, 'r') as f:
    string = f.read()
    index = json.loads(string)
ex = Extractor(save_intermediate_files=False)
config = ex.config.get(report_date='2021-12-31')

recs = []
tickers = list(index.keys())
for ticker in tickers:
    for file in list(index[ticker].keys()):
        doc = path_loc / file
        accounts = ['ACL', 'Loans']    

        for account in accounts:
            if (account in list(index[ticker][file]['output'].keys()) and 
                account in list(config[ticker].accounts.keys())
              ):
              recs.append( (ticker, account, file) )


@pytest.mark.parametrize("ticker, account, file", recs )
def test_select_table(ticker, account, file):
    """This method is run across multiple documents because of the
    inherent difficulties in selecting the correct table.
    """
    desc = index[ticker][file]['desc']
    report_date = index[ticker][file]['report_date']
    loc = path_loc / file

    doc = Doc(Type=desc, FS_Location=loc, report_date=report_date)
    selected_table =  ex.select_table(doc, ticker, account)
    result = True if len(selected_table.__str__()) > 1000 else False
    assert result == True


@pytest.mark.parametrize("ticker, account, file", recs )
def test_extract_process(ticker, account, file):
    """All of the tests will run even if one of them fails.
    """
    desc = index[ticker][file]['desc']
    report_date = index[ticker][file]['report_date']
    account_value = index[ticker][file]['output'][account]
    loc = path_loc / file

    doc = Doc(Type=desc, FS_Location=loc, report_date=report_date)
    rec = ex.execute_extract_process(doc=doc, ticker=ticker)
    val = rec[file][account]
    assert val == account_value


def test_extract_process_no_config_data():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'AXP'
    html_file = 'no_file_here.htm'
    desc = 'EX-99 nothing'
    report_date = '2021-12-31'
    output = {html_file: {}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc, report_date=report_date)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert rec[html_file] == output[html_file]    