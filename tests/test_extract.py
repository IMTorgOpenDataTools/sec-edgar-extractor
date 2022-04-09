import pytest

import os
import shutil
from bs4 import BeautifulSoup

from sec_edgar_extractor.extract import Extractor
from sec_edgar_extractor import utils
from config.config import FirmRecord, AccountRecord







acl = AccountRecord(
    name = 'ACL',
    xbrl = 'FinancingReceivableAllowanceForCreditLosses',
    table_name = 'ALLOCATION OF ALLOWANCE FOR CREDIT LOSSES FOR LOANS',
    table_account = 'Total allowance for credit losses for loans',
    table_column = '',
    scale = '',
    discover_terms = 'allowance',
    search_terms = 'Total allowance for credit|Allowance for credit',
    exhibits = 'EX-99.2'
)
wfc = FirmRecord(
    Firm = 'WFC',
    accounts = {'ACL': acl}
    )
config = {}
config['WFC'] = wfc



def test_check_extractable_html():
    html_doc = {'wfc-99.2': './tests/data/wfc/wfc4qer01-14x22ex992xsuppl.htm'}
    firm = 'WFC'
    account = 'ACL'

    ex = Extractor(config)
    result =  ex.check_extractable_html(html_doc['wfc-99.2'], firm, account)
    tabular_vals = [rec for rec in result if rec[2] == 'tabular']
    cnt = len(tabular_vals)
    assert cnt == 10

def test_select_table():
    html_doc = {'wfc-99.2': './tests/data/wfc/wfc4qer01-14x22ex992xsuppl.htm'}
    firm = 'WFC'
    account = 'ACL'

    ex = Extractor(config)
    selected_table =  ex.select_table(html_doc['wfc-99.2'], firm, account)
    assert selected_table[0]['td_count'] == 1030

def test_format_and_save_table():
    html_doc = {'wfc-99.2': './tests/data/wfc/wfc4qer01-14x22ex992xsuppl.htm'}
    ex = Extractor(config)

    tmp_out = './tests/tmp_out/'
    file_out = 'tbl.html'
    os.makedirs(tmp_out, exist_ok=True)
    with open(html_doc['wfc-99.2'], 'r') as file:
        doc = file.read()
    tbl = BeautifulSoup(doc, "lxml").find_all('table')[2]
    
    ex.format_and_save_table(tbl, tmp_out+file_out)
    idx = os.listdir(tmp_out).index(file_out)
    shutil.rmtree(tmp_out, ignore_errors=True)
    assert idx == 0

def test_single_record_process():
    html_doc = {'wfc-99.2': './tests/data/wfc/wfc4qer01-14x22ex992xsuppl.htm'}
    ex = Extractor(config)
    firm_title = ex.config['WFC'].accounts['ACL'].table_name

    tmp_out = './tests/tmp_out/'
    file_out = 'tbl.html'
    os.makedirs(tmp_out, exist_ok=True)
    with open(html_doc['wfc-99.2'], 'r') as file:
        doc = file.read()
    tbl = BeautifulSoup(doc, "lxml").find_all('table')[20]

    ex.format_and_save_table(tbl, tmp_out+file_out)
    idx = os.listdir(tmp_out).index(file_out)

    tmp_pdf = 'tbl.pdf'
    ex.convert_html_to_pdf(path_html=tmp_out+file_out, path_pdf=tmp_out+tmp_pdf)
    df = ex.get_df_from_pdf(tmp_out+tmp_pdf)
    rows = df.shape[0]

    shutil.rmtree(tmp_out, ignore_errors=True)
    val = ex.get_account_value(df, term=firm_title)
    flt = utils.robust_str_to_float(val)
    assert flt == 13788.0

def test_convert_html_to_pdf():
    assert True

def test_get_df_from_pdf():
    assert True

def test_get_account_value():
    assert True

