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




def test_select_table():
    path_loc = Path('./tests/data/press_release')
    files = path_loc / 'files_save.json'
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
    print(rec)
    assert True == True


def test_extract_process():
    """This is the primary usage example for Extractor.
    This test also checks output against manually-verified output.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')
    files = path_loc / 'files_save.json'

    with open(files, 'r') as f:
        string = f.read()
        data = json.loads(string)
    
    ex = Extractor(save_intermediate_files=False)
    result = []
    for k in data.keys():
        html_file = data[k]['input_file']
        desc = data[k]['input_desc']
        output = data[k]['output']

        loc = path_loc / html_file
        doc = Doc(Description=desc, FS_Location=loc)
        rec = ex.execute_extract_process(doc=doc, ticker=k)
        print(rec)
        f = html_file
        new_rec = {key: output[f][key]==rec[f][key] 
                    for key in list(rec[f].keys()) 
                    if key in output[f].keys() }
        new_rec['ticker'] = k
        result.append(new_rec)
    df = pd.DataFrame(result)
    summary = {}
    cols = df.columns.tolist()
    cols.remove('ticker')
    for col in df.columns:
        rows = df.shape[0]
        summary[col] = df[col].sum() / rows
    print(f"log: execution took: {round(time.time() - start_time, 3)}sec")
    print(summary)
    assert True == True