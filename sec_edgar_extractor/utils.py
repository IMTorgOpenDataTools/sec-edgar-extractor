import os
from pathlib import Path
import subprocess
import mmap
import re
import math

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import warnings

from sec_edgar_extractor.config.config import FirmRecord, AccountRecord, account_defaults


#suppress warnings
warnings.filterwarnings("ignore")





def search_docs_for_terms(download_folder, search_list, ignore_case=True, file_ext='htm'):
    """Search through files for specific regex term(s) and obtain snippet of surrounding text.

    param: download_folder, `dl.download_folder`
    param: search_list, `[r'allowance', r'credit loss']`
    param: ignore_case=True
    param: file_ext='htm'

    return: {file, index, text}
    """
    search_term = '|'.join(search_list)            #gives this r'allowance|credit|loss'
    regex = bytes(search_term, encoding='utf8')    #equivalent to regex = rb"\bcredit|loss\b"
    START = 50
    END = 50
    re_term = re.compile(regex)
    dir_path = str( download_folder / 'sec-edgar-filings')
    total_files = sum([len(files) for r, d, files in os.walk(dir_path)])
    cmd = ['grep','-Ei', search_term, '-rnwl', dir_path] if ignore_case else ['grep','-E', search_term, '-rnwl', dir_path]
    try:
        hits = subprocess.run(cmd, capture_output=True, check=True)
    except Exception as e:
        print(e)
    else:
        files = hits.stdout.decode('utf-8').split('\n')
        files_not_empty = [file for file in files if (file != '' and file_ext in file.split('.')[1])]
        print(f'log: number of files matching criteria: {len(files_not_empty)} of {total_files}')
        results = []
        if len(files_not_empty) > 0:
            for file in files_not_empty:
                with open(file) as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmap_obj:
                        for term in re_term.finditer(mmap_obj):
                            start_idx = term.start() - START if term.start() - START >= 0 else 0
                            end_idx = term.end() + END if term.end() + END < len(mmap_obj) else len(mmap_obj)
                            text = mmap_obj[ start_idx : end_idx].decode('utf8')
                            start_format = START
                            end_format = len(text) - END
                            rec = {'file':file, 
                                   'index': term.start(), 
                                   'text': text, 
                                   'start_format':start_format, 
                                   'end_format':end_format 
                                  }
                            results.append( rec )
            print(f'log: number of lines matching criteria: {len(results)}')
            return results
        else:
            return None



def format_print(text, start=1, end=-1, color='black', is_bold=True):
    """Formatted print of text for use in notebook.

    usage: `format_print('this new text', start=5, end=8)`
    """
    format_text = text[start:end]
    start_text = text[:start]
    end_text = text[end:]
    
    colors = {
        'black' : "30m",
        'red' : "31m",
        'green' : "32m",
        'yellow' : "33m",
        'blue' : "34m",
        'magenta' : "35m",
        'cyan' : "36m",
        'white' : "37m"
        }
    
    pref = "\033["
    reset = f"{pref}0m"
    styled = f'{pref}{1 if is_bold else 0};{colors[color]}' + format_text + reset
    combine = start_text + styled + end_text
    print( combine )



def take_val_from_column(row, col):
    """Get value from column in fixed row, determined by the configuration.
    match col:
        case '<left-most>': return row[0]
        case 'Year ended <MON> <DAY>, / <YYYY>': return row[7]    #TODO:WFC
        case _: return None
    """
    icol = int(col)
    return row[icol]



def correct_row_list(row_list):
    """Correct the input row list so that values can be extracted.
    """
    def separate_items_with_spaces(row_list):
        """Take a list of items and separate into new items if they contain spaces."""
        remove_list = [None, '', '$']
        tmp1 = []
        [tmp1.extend(item.split()) for item in row_list if item not in remove_list]
        return tmp1

    def has_numbers_in_parentheses(s):
        return bool(re.search(r'\(\S+\)', s))

    def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)

    def robust_str_to_float(val):
        """Robustly convert string value to float."""
        if val != '' and has_numbers(val):
            num = float(re.sub("[^0-9.\-]","",val))
            num_1 = -num if has_numbers_in_parentheses(val) else num
            return num_1
        else:
            return val

    separated_row = separate_items_with_spaces(row_list)
    float_row = [robust_str_to_float(item) for item in  separated_row ]
    nonempty_float_row = [item for item in float_row if item!=None]
    return nonempty_float_row


def load_config_account_info(file=None):
    """"Load all account_info and return config(uration) dict.

    TODO:add more defaults 
    """
    def get_default_if_missing(rec, key):
        defaults = account_defaults
        acct = account
        return rec[key] if math.isnan(rec[key]) == False else defaults[acct]['term']

    if file==None:
        file = Path(__file__).parent / 'config/Firm_Account_Info.csv'
    df = pd.read_csv(file, na_values=['NA',''])
    tickers = df['ticker'].value_counts().index
    accounts = df['name'].value_counts().index
    config = {}

    for ticker in tickers:
        tmp_accts = {}
        for account in accounts:
            tmp_df = df[(df['ticker']== ticker) & (df['name']==account)]
            if tmp_df.shape[0] == 1:
                tmp_rec = tmp_df.to_dict('records')[0]
                tmp_acct = AccountRecord(                                
                    name = tmp_rec['name'],
                    xbrl = tmp_rec['xbrl'],
                    table_name = tmp_rec['table_name'],
                    table_account = tmp_rec['table_title'],
                    table_column = tmp_rec['col_idx'],
                    scale = tmp_rec['scale'],
                    discover_terms = get_default_if_missing(rec=tmp_rec, key='discover_terms'),
                    search_terms = get_default_if_missing(rec=tmp_rec, key='search_terms'),
                    exhibits = tmp_rec['exhibits']
                )
                tmp_accts[account] = tmp_acct
            else:
                #print(f'ERROR: tmp_df has {tmp_df.shape[0]} rows')
                continue
        tmp_firm = FirmRecord(
                Firm = ticker,
                accounts = tmp_accts
                )
        config[ticker] = tmp_firm

    return config



def load_documents(documents):
    """Load all staged documents into memory."""
    return_list = []
    for doc in documents:
        txt = doc[1].read_bytes()
        soup = BeautifulSoup(txt, 'lxml')
        return_list.append(soup)
    return return_list