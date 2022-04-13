from pathlib import Path
import pickle
import time
import re

import tidy
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from wkhtmltopdf import wkhtmltopdf #WKHtmlToPdf
import camelot
from rapidfuzz import process, fuzz

from .utils import (
    correct_row_list,
    take_val_from_column,
    load_config_account_info
)




config_template = [
    {'cik': 'number',
        'ticker': 'tkr',
        'accounts': {
            'account1_title': {
                'search_term':'search_term1|search_term2',
                'table':'',
                'exhibit':'',
            }
        }
    },
    ]

class Doc:
    """Interface for the DocumentMetadata namedTuple."""
    def __init__(self, Description, FS_Location):
        self.Description = Description
        self.FS_Location = Path(FS_Location)



class Extractor():
    """Singleton object that maintains config and functionality for extracting data from press-release documents.
    
    TODO:ALL- html_doc can be path or the file string, by passing file string you don't have to re-read for each step of the process
    """

    def __init__(self, config=None, file_path=None):
        if config:
            self.config = config
        elif file_path:
            self.config = load_config_account_info(file_path)
        else:
            self.config = load_config_account_info()


    def execute_extract_process(self, doc, ticker):
        """Run the other class methods in sequence to complete the entire extraction process.
        TODO: replace files if in prod, o/w do not take time to re-run task
        """
        result = {}
        rec = {}
        tkr = ticker
        result_key = doc.FS_Location.name       #TODO: ('|').join(doc.FS_Location.__str__().split('/')[7:9])
        print(f'Directory: {result_key}')

        for acct, acct_rec in self.config[tkr].accounts.items():
            if doc.Description != acct_rec.exhibits: continue
            print(f'Account: {acct}')

            dir = doc.FS_Location.parents[0]
            tbl_output_path = dir / 'tmp' / f'{acct}.html'
            pdf_output_path = dir / 'tmp' / f'{acct}.pdf'
            acct_title = self.config[tkr].accounts[acct].table_account
            check =  self.check_extractable_html(doc.FS_Location, tkr, acct)
            check = True                        #TODO:determine what to check

            if check:
                try:
                    selected_table = self.select_table(doc.FS_Location, tkr, acct)
                    self.format_and_save_table(selected_table[0]['string'], tbl_output_path)
                    self.convert_html_to_pdf(path_html=tbl_output_path, 
                                            path_pdf=pdf_output_path
                                            )
                    df = self.get_df_from_pdf(pdf_output_path)
                    col = self.config[tkr].accounts[acct].table_column
                    val = self.get_account_value(df, term=acct_title, column=col)
                    rec[acct] = val
                except:
                    continue
            else:
                break
        result[result_key] = rec
        return result


    def check_extractable_html(self, html_doc, firm, account):
        """Check if html content is consists of an actual web page, or is not-parsable, such as a html wrapper for images.

        Requirements:
        i) good html
        ii) contains multiple tables
        iii) contains account term

        """
        acct = self.config[firm].accounts[account]
        discover_terms = acct.discover_terms
        with open(html_doc, 'r') as file:
            doc_str = file.read()
        doc = BeautifulSoup(doc_str, 'lxml')

        # rqmt-i)
        Doc = tidy.parseString(
            doc_str,
            output_xhtml=1,
            add_xml_decl=1,
            indent=1,
            tidy_mark=0,
            doctype="transitional",
            )
        err = Doc.errors
        if err:
            print(f'there are {len(err)} errors in this html document.')

        # rqmt-ii)
        tables = doc.find_all('table')
        images = doc.find_all('img')
        if len(images) > len(tables):
            print(f'there are more images {len(images)} than tables {len(tables)} in this document')

        # rqmt-iii)
        result = []
        texts = doc.find_all(text = re.compile(discover_terms))
        for idx, text in enumerate(texts):
            type = 'tabular' if text.find_parent('table') else 'text'
            result.append((idx, text, type))
        return result



    def get_terms_for_calibration(self):
        """Given an iXBRL 10-K/-Q, return a dataframe with all tables' name, term, xbrl account.
        TODO: try this to get terms
        * get all <tr> with term and xbrl account
        * get parent table with accompanying name
        """
        return None



    def select_table(self, doc, firm, account):
        """Given an html file with multiple tables, select a specific table using multiple criterion.

        """
        start_time = time.time()
        acct = self.config[firm].accounts[account]
        search_terms= acct.search_terms
        table_lst = []
        html_string = ()
        with open(doc) as f:
            html = f.read()
            soup = BeautifulSoup(html, 'lxml')
            tags = soup.find_all(text=re.compile(search_terms))

        tbls = []
        for idx, tag in enumerate(tags):
            tbl = tag.find_parent('table')
            if tbl != None:
                tbls.append( {'doc': doc,
                              'len': len(tbl),
                              'td_count': tbl.find_all('td').__len__(),
                              'string': str(tbl)
                             } 
                           )
        #rule-1: take largest table
        if len(tbls) > 0 and tbls != []:
            tbls_sorted = sorted(tbls, key=lambda x:x['len'], reverse=True)
            html_string = tbls_sorted[0]
        #rule-2: take table with most <td>
        if len(tbls) > 0 and tbls != []:
            tbls_sorted = sorted(tbls, key=lambda x:x['td_count'], reverse=True)
            html_string = tbls_sorted[0]
        #TODO: rule-3: take table by name
        #TODO: rule-4: take table with matching account titles

        #result        
        if html_string != ():    
            table_lst.append(html_string)
            html_string = ()
        print(f"log: execution took: {round(time.time() - start_time, 3)}sec")
        return table_lst



    def format_and_save_table(self, table_soup, path_html):
        """"Given a table in a web page, format the table for export to pdf."""
        soup = '<meta charset="utf-8">'+table_soup
        with open(path_html, 'w') as file:
            file.write(soup)
        return True


    def convert_html_to_pdf(self, path_html, path_pdf):
        """Apply `py3-wkhtmltopdf` to html file and convert to pdf."""
        #wkhtmltopdf = WKHtmlToPdf(url = path_html,output_file = path_pdf)
        #wkhtmltopdf.render()
        wkhtmltopdf(url = path_html, output_file = path_pdf)
        return True


    def get_df_from_pdf(self, path_pdf):
        """Apply `` to get a dataframe from a pdf file containing only one table."""
        tables = camelot.read_pdf(str(path_pdf), flavor='stream', pages='1-end', strip_text=['\n'])    #, column_tol=10)
        df = tables[0].df
        df_edit = df.replace({'\t': ' '}, regex=True)
        return df_edit


    def get_account_value(self, df, column, term='Total allowance for credit losses', display_terms=3, index_term=0):
        """Given a dataframe and target context, extract the specific account value.
        TODO: integrate utils.robust_str_to_float(val)
        TODO: add index column that has '/' to denote carriage return
        TODO: add to include column more than <left-most>
        """
        lst = df.loc[:,0].to_list()
        idx_terms = process.extract(term, lst, scorer=fuzz.WRatio, limit=display_terms)
        idx = idx_terms[0][2]
        row = df.loc[idx].tolist()[1:] 
        fixed_row = correct_row_list(row)
        val = take_val_from_column(fixed_row, column)    
        return val