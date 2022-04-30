import sys
from pathlib import Path
import pickle
import time
import re
import functools

import tidy
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pdfkit
#from wkhtmltopdf import wkhtmltopdf #WKHtmlToPdf
import camelot
from rapidfuzz import process, fuzz

from .utils import (
    correct_row_list,
    take_val_from_column,
    load_config_account_info
)

#change default recursion depth until error
#sys.setrecursionlimit(100)




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
    def __init__(self, Type, FS_Location):
        self.Type = Type
        self.FS_Location = Path(FS_Location)



class Extractor():
    """Singleton object that maintains config and functionality for extracting data from press-release documents.
    If selected using `save_intermediate_files`, save intermediate files in a path the same name as the extracted file.
    
    TODO:ALL- html_doc can be path or the file string, by passing file string you don't have to re-read for each step of the process
    """

    def __init__(self, config=None, file_path=None, save_intermediate_files=False):
        if config:
            self.config = config
        elif file_path:
            self.config = load_config_account_info(file_path)
        else:
            self.config = load_config_account_info()
        
        self.save_intermediate_files = save_intermediate_files



    def execute_extract_process(self, doc, ticker):
        """Run the other class methods in sequence to complete the entire extraction process.
        TODO: replace files if in prod, o/w do not take time to re-run task
        """
        result = {}
        rec = {}
        tkr = ticker
        result_key = doc.FS_Location.name       #TODO: ('|').join(doc.FS_Location.__str__().split('/')[7:9])
        print(f'Directory: {result_key}')

        hash_map_of_tables_in_pdf = {}
        global clean_up
        clean_up = []
        dir = doc.FS_Location.parents[0]

        if not tkr in self.config.keys():
            result[result_key] = {}
            return result

        for acct, acct_rec in self.config[tkr].accounts.items():
            if doc.Type != acct_rec.exhibits or type(acct_rec.table_account) != str:
                continue
            print(f'Account: {acct}')

            if self.save_intermediate_files:
                itermediate_dir = doc.FS_Location.stem

            else:
                itermediate_dir = 'tmp'
            output_path = dir / itermediate_dir 
            output_path.mkdir(parents=True, exist_ok=True)
            tbl_output_path = output_path / f'{acct}.html'
            pdf_output_path = tbl_output_path.with_suffix('.pdf')

            acct_title = self.config[tkr].accounts[acct].table_account
            #check =  self.check_extractable_html(doc.FS_Location, tkr, acct)
            check = True
            if check:
                try:
                    selected_table = self.select_table(doc.FS_Location, tkr, acct)
                    tbl_hash = hash(selected_table)
                    if tbl_hash not in hash_map_of_tables_in_pdf.keys():
                        self.format_and_save_table(selected_table, tbl_output_path)    #previously: selected_table[0]['string']
                        self.convert_html_to_pdf(path_html=tbl_output_path, 
                                                path_pdf=pdf_output_path
                                                )
                        hash_map_of_tables_in_pdf[tbl_hash] = pdf_output_path
                    else:
                        pdf_output_path = hash_map_of_tables_in_pdf[tbl_hash] 
                    df = self.get_df_from_pdf_or_file(pdf_output_path)
                    col = self.config[tkr].accounts[acct].table_column  
                    fixed_row = self.get_account_row(df, term=acct_title)    #TODO: chg to col_idx
                    val = take_val_from_column(fixed_row, col)
                    rec[acct] = val
                except Exception as e:
                    print(f"Exception: {e}")
                    continue
            else:
                continue
        result[result_key] = rec
        if not self.save_intermediate_files:
            [Path.unlink(file) for file in clean_up]
        return result


    def check_extractable_html(self, html_doc, firm, account):
        """Check if html content is consists of an actual web page, or is not-parsable, such as a html wrapper for images.

        Requirements:
        i) good html
        ii) contains multiple tables
        iii) contains account term

        """
        acct = self.config[firm].accounts[account]
        discover_terms = acct.table_name            #acct.discover_terms
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
        if (len(images) > len(tables)) or (len(tables)==0):
            print(f'there are more images {len(images)} than tables {len(tables)} in this document')
            return False

        # rqmt-iii)
        result = []
        texts = doc.find_all(text = re.compile(discover_terms, re.I))
        for idx, text in enumerate(texts):
            if len(result) == 0:
                type = 'tabular' if text.find_parent('table') else 'text'
                result.append((idx, text, type))
            else:
                break
        if len(result)>0:
            return True
        else:
            return False



    def get_terms_for_calibration(self):
        """Given an iXBRL 10-K/-Q, return a dataframe with all tables' name, term, xbrl account.
        TODO: try this to get terms
        * get all <tr> with term and xbrl account
        * get parent table with accompanying name
        """
        return None



    def select_table(self, doc, firm, account):
        """Given an html file with multiple tables, select a specific table using multiple criterion.
        TODO: two possibilities
        * (local minima) C Total loans, net - not getting CITIGROUP CONSOLIDATED BALANCE SHEET
        * (sibling)
        algorithm:
        i) recursively go through siblings looking for a table
        ii) move up to parent, look for table, then do (i)
        iii) if table is found .find_all(text=re.compile(table_acct))
        iv) if multiple tables with table_acct found, choose the first
        """

        def remove_unuseful_tables(tag):
            result = None
            if tag.parent.name == 'a':
                pass
            else:
                result = tag
            return result


        def verify_table(tag, table_acct):
            """Verify this is the correct table containing the desired account title."""
            regex = re.compile('[^a-zA-Z ]')
            #cond-1: bs4 table
            if hasattr(tag,'name') and type(tag) in [bs4.element.Tag, bs4.element.NavigableString]:
                if tag.name == 'table':
                    #cond-2: multiple rows
                    rows = tag.find_all('tr')
                    if len(rows) > 5:
                        tbl = tag
                        #cond-3: correct account title TODO:table_acct is difficult to get, using `text=table_acct` must be exact, but using `text=re.compile(table_acct)` requires characters to be appropriately backspaced
                        #TODO:what about acct.title with multiple lines
                        escaped_acct = re.escape(table_acct)
                        accts = tbl.find_all(text=re.compile(escaped_acct))
                        #intermediate = [regex.sub('', acct.strip()) for acct in accts]
                        correct_accts = [acct for acct in accts if acct != None]
                        if correct_accts != []:
                            return True, len(correct_accts), tbl
            return False, None, None


        def check_children_for_table(tag, table_acct):
            """Checks children and returns table with most occurrences."""
            fail = False, None, None
            result = []
            if hasattr(tag, 'find_all'):
                tbls = tag.find_all('table')
                if len(tbls) > 0:
                    for tbl in tbls:
                        rec = verify_table(tbl, table_acct)
                        if rec[0] == True:
                            result.append(rec)
            match len(result):
                case 0:
                    return fail
                case 1:
                    return result[0]
                case _:
                    tbls_sorted = sorted(result, key=lambda x:x[1], reverse=True)
                    return tbls_sorted[0]

        @functools.cache
        def check_tag_and_children_for_table(tag, table_acct):
            memoize = {}  #tag and children
            current_tag = verify_table(tag, table_acct)
            children_tag = check_children_for_table(tag, table_acct)
            if current_tag[0]:
                return current_tag
            elif children_tag[0]:
                return children_tag
            else:
                return False, None, None


        def find_table_recurse(tag, table_acct):
            """Get the correct table if it exists."""
            try:
                current_tag = check_tag_and_children_for_table(tag, table_acct)
                siblings = tag.next_siblings
                parent = tag.parent
                if current_tag[0]:
                    return current_tag
                elif siblings:
                    for sib in siblings:
                        sib_and_children = check_tag_and_children_for_table(sib, table_acct)
                        if sib_and_children[0]:
                            return sib_and_children
                else:
                    pass
                tbl = find_table_recurse(parent, table_acct)
                if tbl[0]: 
                    return tbl
            except RecursionError as recerr:
                print('Maximum recursion limit reached')


        def progressive_text_search(term):
            """
            Progressively more general search for text:
            i) exact NavigableString
            ii) subtext within text
            iii) text broken or separated among tags (ie <div>Table</div><div>Name<div>)
            """
            nested = acct.table_name.split()
            terms = [term, re.compile(re.escape(term)), nested]
            result = []
            for term in terms:
                if type(term) != list:
                    possible_tags1 = soup.find_all(text=term)                                                                                                        #TODO:maybe search by multiple terms (table, account, column)
                    possible_tags2 = [remove_unuseful_tables(tag) for tag in possible_tags1]
                    possible_tags3 = process.extract(acct.table_name, possible_tags2, scorer=fuzz.WRatio, limit=3)
                    tags = [tag[0] for tag in possible_tags3]
                else:
                    nested_items = [soup.find_all(text=re.compile(sub_text)) for sub_text in term]
                    [table_lst.extend(item) for item in nested_items if item != [] ]
                    tags = list(set(table_lst))
                if len(tags) > 0:
                    return tags

        def nested_loops(tags_table_name, tags_account):
            """Nested loops which use a return to break"""
            for tbl_name in tags_table_name:
                 for tbl_name_parent in tbl_name.parents:
                     for account in tags_account:
                         for account_parent in account.parents:
                             if hasattr(tbl_name_parent, 'name') and hasattr(account_parent, 'name'):
                                 if tbl_name_parent.name == 'table' and account_parent.name == 'table':
                                     if tbl_name_parent == account_parent:
                                         selected_tables.append( tbl_name_parent )
                                         return True
            return False



        start_time = time.time()
        acct = self.config[firm].accounts[account]
        table_lst = []
        selected_tables = []
        with open(doc) as f:
            html = f.read()
            soup = BeautifulSoup(html, 'html.parser')    #only this parser has access to Tag.sourceline, Tag.sourcepos (if needed)
            # find tags
            tags_table_name = progressive_text_search( acct.table_name )
            tags_account = progressive_text_search( acct.table_account )
            # find table by using parents of both table_name and account
            rtn = nested_loops(tags_table_name, tags_account)
            # find the table recursively, as a last resort (its slow)
            if rtn == False and len(selected_tables) == 0:
                for tag in tags_table_name:
                    tbl = find_table_recurse(tag, acct.table_account)
                    if tbl[0]:
                        selected_tables.append(tbl[2])

        unique_tables = list(set(selected_tables))
        print(len(unique_tables))
        print(f"log: execution took: {round(time.time() - start_time, 3)}sec")
        return unique_tables[0].__str__()


    def format_and_save_table(self, table_soup, path_html):
        """"Given a table in a web page, format the table for export to pdf."""
        soup = '<meta charset="utf-8">'+table_soup
        with open(path_html, 'w') as file:
            file.write(soup)
        clean_up.append(path_html)
        return True


    def convert_html_to_pdf(self, path_html, path_pdf):
        """Apply `py3-wkhtmltopdf` to html file and convert to pdf."""
        #wkhtmltopdf = WKHtmlToPdf(url = path_html,output_file = path_pdf)
        #wkhtmltopdf.render()
        #fix:Blocked access to file
        options = {
            "enable-local-file-access": True
            }
        pdfkit.from_file(path_html.__str__(), path_pdf.__str__(), options=options)
        clean_up.append(path_pdf)
        #wkhtmltopdf(url = path_html, output_file = path_pdf)
        return True


    def get_df_from_pdf_or_file(self, path_pdf):
        """Apply `camelot` to get a dataframe from a pdf file containing only one table.
        This will also 'cache' the dataframe to a csv, and load it, if available.
        """
        path_csv = path_pdf.with_suffix('.csv')
        file = Path(path_csv)
        if file.exists():
            df_edit = pd.read_csv(path_csv)
        else:
            tables = camelot.read_pdf(str(path_pdf), flavor='stream', pages='1-end', strip_text=['\n'], edge_tol=10)    #, column_tol=10, edge_tol=10)
            df = tables[0].df
            df_edit = df.replace({'\t': ' '}, regex=True)
            df_edit.to_csv(path_csv, index=False)
            clean_up.append(path_csv)
        return df_edit


    def get_account_row(self, df, term='Total allowance for credit losses', display_terms=2, index_term=0):
        """Given a dataframe and target context, extract the specific account value.
        TODO: add index column that has '/' to denote carriage return
        TODO:what about acct.title with multiple lines
        TODO: add to include column more than <left-most>
        TODO: find where some rows are dropped from df
        """
        def process_row_list(idx_term, offset):
            idx = idx_term[2] + offset
            row = [item for item in df.loc[idx].tolist()[1:] if type(item)==str]
            fixed_row = correct_row_list(row)
            return fixed_row

        OFFSETS= [0,1]
        def prepare_table_row(df, term):
            lst = [str(item) for item in df.iloc[:,0].to_list()]
            idx_terms = process.extract(term, lst, scorer=fuzz.WRatio, limit=display_terms)
            for offset in OFFSETS:
                for idx_term in idx_terms:
                    fixed_row = process_row_list(idx_term, offset)
                    if fixed_row != []:
                        return fixed_row
        
        fixed_row = prepare_table_row(df, term)    
        return fixed_row