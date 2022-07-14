import pytest

import os
from pathlib import Path
import json
import shutil
from bs4 import BeautifulSoup
import pandas as pd

from sec_edgar_extractor.extract import Doc, Extractor
from sec_edgar_extractor import utils
#from sec_edgar_extractor.config import FirmRecord, AccountRecord
from sec_edgar_extractor.config.config import FirmRecord, AccountRecord





# config
acl_topic = AccountRecord(
    timeperiod = (pd.to_datetime('2021-Q2'), pd.Timestamp.now().date() ),
    name = 'ACL',
    xbrl = 'FinancingReceivableAllowanceForCreditLosses',
    table_name = 'ALLOCATION OF ALLOWANCE FOR CREDIT LOSSES FOR LOANS',
    table_account = 'Total allowance for credit losses for loans',
    table_column = 0,
    scale = 'millions',
    discover_terms = 'allowance',
    search_terms = 'Total allowance for credit|Allowance for credit',
    exhibits = 'EX-99.2'
)
wfc = FirmRecord(
    Firm = 'WFC',
    accounts = {'ACL': acl_topic}
    )
rec = {'WFC': wfc}
config = utils.Config(firm_records=rec)



def test_check_extractable_html():
    html_doc = {'PNC': {'desc': 'EX-99.1', 'path': './tests/data/press_release/a2021_0601xrlsxpncbbvale.htm', 'report_date': '2021-06-01'},
                'WFC': {'desc': 'EX-99.2', 'path': './tests/data/press_release/wfc4qer01-14x22ex992xsuppl.htm', 'report_date': '2021-12-31'}
                }
    account = 'ACL'
    ex = Extractor()

    results = []
    for firm, meta in html_doc.items():
        doc = Doc(Type=meta['desc'], 
                    FS_Location=meta['path'], 
                    report_date=meta['report_date']
                    )
        out =  ex.check_extractable_html(doc, firm, account)
        results.append(out)

    assert results == [False, True]


def test_select_table():
    html_doc = {'PNC': {'desc': 'EX-99.1', 'path': './tests/data/press_release/q420inancialhighlightsandn.htm', 'report_date': '2021-07-01'},
                'WFC': {'desc': 'EX-99.2', 'path': './tests/data/press_release/wfc4qer01-14x22ex992xsuppl.htm', 'report_date': '2021-12-31'},
                'C': {'desc': 'EX-99.2', 'path': './tests/data/press_release/c-20211231xex99d2.htm', 'report_date': '2021-12-31'}
                }
    account = 'ACL'
    ex = Extractor()

    results = []
    for firm, meta in html_doc.items():
        doc = Doc(Type=meta['desc'], 
                    FS_Location=meta['path'], 
                    report_date=meta['report_date']
                    )
        selected_table = ex.select_table(doc, firm, account)
        results.append( len(selected_table.__str__()) )

    assert results == [87834, 144616, 279219]


def test_format_and_save_table():
    html_doc = {'WFC': {'desc': 'EX-99.2', 'path': './tests/data/press_release/wfc4qer01-14x22ex992xsuppl.htm', 'report_date': '2021-12-31'}}
    ex = Extractor(config)

    tmp_out = Path('./tests/tmp_out/')
    file_out = 'tbl.html'
    os.makedirs(tmp_out, exist_ok=True)
    with open(html_doc['WFC']['path'], 'r') as file:
        doc = file.read()
    tbl = BeautifulSoup(doc, "lxml").find_all('table')[20]
    
    ex.format_and_save_table(tbl, tmp_out/file_out)
    idx = os.listdir(tmp_out).index(file_out)
    shutil.rmtree(tmp_out, ignore_errors=True)
    assert idx == 0


def test_single_record_process():
    html_doc = {'WFC': {'desc': 'EX-99.2', 'path': './tests/data/press_release/wfc4qer01-14x22ex992xsuppl.htm', 'report_date': '2021-12-31'}}
    ex = Extractor(config)
    report_date = html_doc['WFC']['report_date']
    firm_title = ex.config.get(report_date)['WFC'].accounts['ACL'].table_account

    tmp_out = Path('./tests/tmp_out/')
    file_out = 'tbl.html'
    os.makedirs(tmp_out, exist_ok=True)
    with open(html_doc['WFC']['path'], 'r') as file:
        doc = file.read()
    tbl = BeautifulSoup(doc, "lxml").find_all('table')[20]

    ex.format_and_save_table(tbl, tmp_out/file_out)
    idx = ex.config.get(report_date)['WFC'].accounts['ACL'].table_column

    tmp_pdf = 'tbl.pdf'
    ex.convert_html_to_pdf(path_html=tmp_out/file_out, 
                            path_pdf=tmp_out/tmp_pdf
                            )
    df = ex.get_df_from_pdf_or_file(tmp_out/tmp_pdf)        #TODO: camelot cuts-off 'Total' in 'Total allowance for credit losses'

    shutil.rmtree(tmp_out, ignore_errors=True)
    fixed_row = ex.get_account_row(df, term=firm_title)
    val = utils.take_val_from_column(fixed_row, idx)
    assert val == 13788.0


def test_convert_html_to_pdf():
    assert True

def test_get_df_from_pdf():
    assert True

def test_get_account_value():
    assert True

