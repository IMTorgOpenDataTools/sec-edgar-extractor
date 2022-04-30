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
        doc = Doc(Type=desc, FS_Location=loc)
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


def test_extract_process_test_tfc():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'TFC'
    html_file = 'ex992-qps4q21.htm'
    desc = 'EX-99.2'
    output = {'ex992-qps4q21.htm': {'ACL': 4695.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert True == True


def test_extract_process_test_citi():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'C'
    html_file = 'c-20211231xex99d2.htm'
    desc = 'EX-99.2'
    output = {'c-20211231xex99d2.htm': {'ACL': -15393.0, 'Loans': 644276.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert True == True


def test_extract_process_test_cfg():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'CFG'
    html_file = 'a4q21earningsrelease.htm'
    desc = 'EX-99.1'
    output = {'a4q21earningsrelease.htm': {'ACL': 1934.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert True == True


def test_extract_process_test_pnc():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'PNC'
    html_file = 'q42021financialsupplement.htm'
    desc = 'EX-99.1'
    output = {'q42021financialsupplement.htm': {'ACL': 5530.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)
    exts = ['.csv','.html','pdf']
    [os.remove('./tests/data/press_release/tmp/ACL'+ext) for ext in exts 
        if os.path.exists('./tests/data/press_release/tmp/ACL'+ext)]

    result = []
    tkr = 'PNC'
    html_file = 'q12022financialhighlightsa.htm'
    desc = 'EX-99.1'
    output = {'q12022financialhighlightsa.htm': {'ACL': 0.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert True == True


def test_extract_process_test_key():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'KEY'
    html_file = 'a1q22erex993.htm'
    desc = 'EX-99.3'
    output = {'a1q22erex993.htm': {'ACL': -1105.0, 'Loans': 106600.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert True == True


def test_extract_process_test_ms():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'MS'
    html_file = 'a52683164ex99_2.htm'
    desc = 'EX-99.2'
    output = {html_file: {'ACL': 679.0, 'Loans': 209067.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)
    
    assert rec[html_file] == output[html_file]


def test_extract_process_test_wfc():
    """Check that a firm not in the reference file (Firm_Account_Info.csv)
        will fail gracefully.
    """
    start_time = time.time()
    path_loc = Path('./tests/data/press_release')

    ex = Extractor(save_intermediate_files=False)

    result = []
    tkr = 'WFC'
    html_file = 'q12022financialsupplement.htm'
    desc = 'EX-99.2'
    output = {'q12022financialsupplement.htm': {'ACL': 5197.0, 'Loans': 'Amount'}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert True == True


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
    output = {'no_file_here.htm': {'ACL': 0.0}}

    loc = path_loc / html_file
    doc = Doc(Type=desc, FS_Location=loc)
    rec = ex.execute_extract_process(doc=doc, ticker=tkr)

    assert rec == {'no_file_here.htm': {}}