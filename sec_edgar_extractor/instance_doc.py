"""
Parse SEC 8-K Earnings Release Instance Document for extractable information.
"""
__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from pathlib import Path
import re
from tabnanny import check

import bs4
import pandas as pd





class Instance_Doc:

    def __init__(self):
        pass


    def get_quarterly_value(self, df, xbrl_concept):
        """Given the InstanceDoc dataframe and the required xbrl_concept, 
        return the value associated information.

        TODO: implement this later
        """
        return None


    def get_account_table_position(self, soup, xbrl_concept_id):
        """Given bs4-ingested iXBRL (10-K/-Q), obtain the table position (row/col) 
        of the xbrl concept.

        Usage: df['id'].map(lambda x: self.get_account_table_position(soup, x))
        """
        rec = {
            'id': xbrl_concept_id,
            'account_title': None,
            'value': None,
            'col_idx': None,
            #'row': None
            }
        if xbrl_concept_id == None:
            return rec
        # get target account row
        trgt = soup.find(re.compile(".*"), {'id': xbrl_concept_id})
        rows = [tag for tag in trgt.parents if tag.name == 'tr']
        if len(rows) > 0:
            row = rows[0]
        else:
            return rec
        account_tag = row.find('td')

        tds = row.findChildren('td')
        col_idx = [(idx, td) for idx, td in enumerate(tds) if trgt.text in td.text][0][0]

        # if title is indented then the title is a continuation of a higher row
        if account_tag.get('style').find('padding'):
            check_indent = account_tag.get('style').split('padding:')[1].split(';')[0]
            if len(check_indent) > 8:
                section_tag = row.previous_sibling.find_all('td')[0]
                account_title = section_tag.text + '|' +  account_tag.text
            else:
                account_title = account_tag.text
        else:
            account_title = account_tag.text
        rec = {
            'id': xbrl_concept_id,
            'account_title': account_title,
            'value': trgt.text,
            'col_idx': col_idx,
            #'row': row
            }
        return rec


    def create_xbrl_dataframe(self, file_xml):
        """Given the 10-K XBRL Instance Doc (`_html.xml`), merge Concepts with ContextRef(erences),
        and return a dataframe.
        """
        soup = bs4.BeautifulSoup(file_xml, 'xml')
        tags = soup.find_all(re.compile(".*"))
        dei_xbrl = []
        gaap_xbrl = []
        context_dims = []
        tables = []

        #us-gaap, ifrs-full, dei, or srt
        def cond(tag):
            return True if tag.prefix == 'dei' else False
        tags_document = [tag for tag in tags if cond(tag)]

        def cond(tag): 
            return True if tag.prefix == 'us-gaap' and tag.get('contextRef') and len(tag.text) < 200 else False
        tags_xbrl = [tag for tag in tags if cond(tag)]

        def cond(tag):
            return True if tag.name == 'context' else False
        tags_contexts = [tag for tag in tags if cond(tag)]

        #def cond(tag):
        #    return True if tag.prefix == 'us-gaap' and 'TextBlock' in tag.name and 'table' in tag.text else False
        #tags_tables = [tag for tag in tags if cond(tag)]
        for tag in tags_document:
            rec = {
                'name': tag.name,
                'value': tag.text
                }
            dei_xbrl.append(rec)

        for tag in tags_xbrl:
            rec = {
                'id': tag.get('id'),
                'concept': tag.name,
                'contextRef': tag.get('contextRef'),
                'unitRef': tag.get('unitRef'),
                'value': tag.text,
                'decimals': tag.get('decimals')
                }
            gaap_xbrl.append(rec)

        for tag in tags_contexts:
            start = tag.find_all('startDate')
            instant = tag.find_all('instant')
            if start != []:
                start_date = start[0].text
                end_date = tag.find('endDate').text
            elif instant != []:
                start_date = instant[0].text
                end_date = ''
            children = tag.find_all(re.compile(".*"))
            dims = [child for child in children if (child.name=='explicitMember' and child.get('dimension'))]
            if dims != []:
                for dim in dims:
                    rec = {
                        'id': tag.get('id'),
                        'dimension': dim.get('dimension'),
                        'value': dim.text,
                        'start': start_date,
                        'end': end_date,
                        }
                    context_dims.append(rec)
            else:
                rec = {
                    'id': tag.get('id'),
                    'dimension': '',
                    'value': '',
                    'start': start_date,
                    'end': end_date,
                    }
                context_dims.append(rec)


        df_doc = pd.DataFrame(dei_xbrl)
        df_xbrl = pd.DataFrame(gaap_xbrl)
        df_dim = pd.DataFrame(context_dims)
        df_combine = df_xbrl.merge(df_dim, left_on='contextRef', right_on='id', how='outer', suffixes=['_concept', '_context'])
        df_combine['start'] = pd.to_datetime(df_combine['start'], format='%Y-%m-%d')
        df_combine['end'] = pd.to_datetime(df_combine['end'], format='%Y-%m-%d')
        return df_doc, df_combine



    def combine_all_tags_in_dataframe(self, file_path_instance, file_path_ixbrl):
        """

        The only way to map xbrl to the account title is using the value as the unique key (weak assumption)
        The correct way is to get the iXBRL file, and `ix:nonfraction` tag for target value, then match that id with <us-gaap:[CONCEPT] tag using `df_xbrl` 

        """
        with open(file_path_instance, 'r') as f:
            file_htm_xml = f.read()
        with open(file_path_ixbrl, 'r') as f:
            file_ixbrl = f.read()

        df_doc, df_combine = self.create_xbrl_dataframe(file_htm_xml)

        soup = bs4.BeautifulSoup(file_ixbrl, 'html.parser')
        df_tmp = df_combine.iloc[0:100,:]
        result = df_tmp['id_concept'].map(lambda id_concept: self.get_account_table_position(soup, id_concept))
        df_10k = pd.DataFrame.from_dict(result.tolist())
        df = df_tmp.merge(df_10k, left_on='id_concept', right_on='id', how='inner', suffixes=['_comb', '_table'])

        return df


    def prepare_config_file(self, xbrl_concept, file_path_instance, file_path_ixbrl, file_path_earnings_release):
        """Create the config (Firm_Acct_Info) file.

        This works by comparing the current 10k/q against the previous 8k for the given xbrl concept:
        * get current 10k/q concept value and table account title
        * get previous 8k row indexed by account title and containing the current 10k/q value
        * get row's position in table, and table in document

        Usage: 
        xbrl_concept = 'us-gaap:FinancingReceivableAllowanceForCreditLosses'
        ...
        """
        
        with open(file_path_instance, 'r') as f:
            file_htm_xml = f.read()
        with open(file_path_ixbrl, 'r') as f:
            file_ixbrl = f.read()
        with open(file_path_earnings_release, 'r') as f:
            file_earnings = f.read()

        df_doc, df = self.create_xbrl_dataframe(file_htm_xml)
        meta = df[(df['concept'] == xbrl_concept) & (df['start']=='2022-03-31') & (df['dimension']=='')]
        if meta.shape[0] == 1:
            id_concept = meta.id_concept.values[0]

        soup_ixbrl = bs4.BeautifulSoup(file_ixbrl, 'html.parser') 
        tbl_position = self.get_account_table_position(soup_ixbrl, id_concept)

        soup_earnings = bs4.BeautifulSoup(file_earnings, 'html.parser')
        split = tbl_position['account_title'].split('|')
        if len(split)>0:
            title = split[1]
        else:
            title = split[0]
        title_instances = soup_earnings.find_all( string=re.compile(title, re.I) )
        row_candidates = []
        for title in title_instances:
            #check if it is within table
            check_tbl = [tag for tag in title.parents if tag.name == 'table']
            if check_tbl != []:
                #get row and find account value
                rows = [tag for tag in title.parents if tag.name == 'tr' and tbl_position['value'] in tag.text]
                row_candidates.extend(rows)

        #TODO: use utils' functions to parse this better, or integrate with them
        print( f'{row_candidates[0].text}')   #'Ending balance$4,558\xa0$4,868\xa0$5,355\xa0$5,730\xa0$4,714\xa0'

        line = row_candidates[0].text
        line_columns = line.replace(title,'').replace('\xa0',' ').split(' ')
        item = [col for col in line_columns if tbl_position['value'] in col][0]
        column = line_columns.index(item)

        table = [tag for tag in row_candidates[0].parents if tag.name == 'table'][0]
        table_name = table.previous_sibling.text.strip()

        def get_scale(table):
            if 'thousand' in table.text:
                return 'thousand'
            elif 'million' in table.text:
                return 'million'
            elif 'billion' in table.text:
                return 'billion'
        scale = get_scale(table)     #TODO: improve

        rec = {
            'cik': '',
            'ticker': '',
            'xbrl_concept': xbrl_concept,
            'table_name': table_name,
            'table_title': title,
            'tbl_col_idx': column,
            'scale': scale,
            'exhibit': ''
            }

        return rec