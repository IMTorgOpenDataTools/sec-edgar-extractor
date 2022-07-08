"""
Load documentation from us-gaap taxonomy into index-able structures.
"""
__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


from pathlib import Path
import re
from tabnanny import check

import bs4
import pandas as pd





class Documentation:
    '''Load documentation from us-gaap taxonomy into index-able structures.
    
    Files needed (placed in `sec_edgar_extractor/config/`):
    * us-gaap-doc-2022.xml - tag descriptions
    * us-gaap-ref-2022.xml - codification references
    '''

    def __init__(self):
        self.desc_path = Path(__file__).parent / 'config/us-gaap-doc-2022.xml'
        self.codif_path = Path(__file__).parent / 'config/us-gaap-ref-2022.xml'
        #TODO: save attr data to pickle and load upon initialization
        self.xbrl_description = None
        self.xbrl_reference_arcs = None
        self.xbrl_codification= None

    def load_documents(self):
        with open(self.desc_path, 'r') as f:
            xml_desc = f.read()
        with open(self.codif_path, 'r') as f:
            xml_codif = f.read()

        # descriptions    
        soup = bs4.BeautifulSoup(xml_desc, 'xml')
        tags = soup.find_all(re.compile('.*'))
        labels = [item for item in tags if item.name == 'label']
        recs = []
        for lab in labels:
            rec = {
                'xbrl_tag': lab['xlink:label'].split('lab_')[1],
                'xbrl_tag_description': lab.text
                }
            recs.append(rec)
        self.xbrl_description = pd.DataFrame(recs)

        # reference arcs
        soup = bs4.BeautifulSoup(xml_codif, 'xml')
        tags = soup.find_all(re.compile('.*'))
        reference_arcs = [item for item in tags if item.name == 'referenceArc']
        recs = []
        for loc in reference_arcs:
            rec = {
                'xbrl_tag': loc['xlink:from'].split('loc_')[1],
                'link_to': loc['xlink:to']
            }
            recs.append(rec)
        df_tmp = pd.DataFrame(recs)
        df_grp = pd.DataFrame( df_tmp.groupby('xbrl_tag')['link_to'].apply(list) )
        df_grp['count'] = df_tmp.groupby('xbrl_tag').size()
        df_grp.sort_values(by='count', ascending=False, inplace=True)
        self.xbrl_reference_arcs = df_grp

        # codification references
        references = [item for item in tags if item.name == 'reference']
        recs = []
        for idx, ref in enumerate(references):
            rec = {
                'label': ref['xlink:label'],
                'publisher': ref.findChild('ref:Publisher').text if ref.findChild('ref:Publisher') else None,
                'name': ref.findChild('ref:Name').text if ref.findChild('ref:Name') else None,
                'code_topic': ref.findChild('codification-part:Topic').text if ref.findChild('codification-part:Topic') else None,
                'code_subtopic': ref.findChild('codification-part:SubTopic').text if ref.findChild('codification-part:SubTopic') else None,
                'section': ref.findChild('ref:Section').text if ref.findChild('ref:Section') else None,
                'paragraph': ref.findChild('ref:Paragraph').text if ref.findChild('ref:Paragraph') else None,
                'code_uri': ref.findChild('codification-part:URI').text if ref.findChild('codification-part:URI') else None
            }
            recs.append(rec)
        self.xbrl_codification = pd.DataFrame(recs)

        return True


    def get_records(self, xbrl_labels):
        lst = list(xbrl_labels)
        df_tag = self.xbrl_description[self.xbrl_description['xbrl_tag'].isin(lst)]
        df_ref = pd.merge(df_tag, self.xbrl_reference_arcs, on='xbrl_tag')
        df_left = df_ref.explode('link_to', ignore_index=True)
        df_code = pd.merge(df_left, self.xbrl_codification, left_on='link_to', right_on='label')
        df_code.drop(columns=['link_to','count','label'], inplace=True)
        doc_records = df_code.to_dict('records')
        return doc_records