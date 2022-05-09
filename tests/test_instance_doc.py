import pytest
from pathlib import Path
import time

import pandas as pd

from sec_edgar_extractor import instance_doc



def test_instance_extract():
    dir = './tests/data/instance_doc'
    file_instance = 'pnc-20220331_htm.xml'
    file_ixbrl = 'pnc-20220331.htm'             # this file is from the browser xbrl view > 'Open as HTML' which is considerably larger (7.2MB) versus when you download the file directly (66KB), url: `https://www.sec.gov/Archives/edgar/data/713676/000071367622000047/pnc-20220331.htm`
    file_earnings_release = 'q12022financialsupplement.htm'

    file_path_instance = Path(dir) / file_instance
    file_path_ixbrl= Path(dir) / file_ixbrl
    topic = 'AllowanceForCreditLosses'

    start_time = time.time()
    inst_doc = instance_doc.Instance_Doc()
    inst_doc.get_tags(file_path_instance, file_path_ixbrl)
    print(f"log: execution took: {round(time.time() - start_time, 3)}sec")

    assert True == True


def test_prepare_config_file():
    dir = './tests/data/instance_doc'
    file_instance = 'pnc-20220331_htm.xml'
    file_ixbrl = 'pnc-20220331.htm'             # this file is from the browser xbrl view > 'Open as HTML' which is considerably larger (7.2MB) versus when you download the file directly (66KB), url: `https://www.sec.gov/Archives/edgar/data/713676/000071367622000047/pnc-20220331.htm`
    file_earnings_release = 'q12022financialsupplement.htm'

    file_path_instance = Path(dir) / file_instance
    file_path_ixbrl= Path(dir) / file_ixbrl
    file_path_earnings = Path(dir) / file_earnings_release
    xbrl_concept = 'FinancingReceivableAllowanceForCreditLosses'

    inst_doc = instance_doc.Instance_Doc()
    rec = inst_doc.prepare_config_file(xbrl_concept, file_path_instance, file_path_ixbrl, file_path_earnings)

    assert True == True


def test_get_quarterly_value():
    """This is the workflow that should be reproduced for getting data.

    * download InstDoc with: Type 'XML' and Document '*_htm.xml'
    * create_xbrl_dataframe(file_xml)
    * find xbrl tag in dataframe, filter on dimensions  
    """
    xbrl_rqmt = {
        'xbrl_concept': 'FinancingReceivableAllowanceForCreditLosses',
        'dimension': '',
        'value_context': '',
        'start': pd.to_datetime('2022-03-31'),
        'end': pd.to_datetime('')
        }

    dir = './tests/data/instance_doc'
    file_instance = 'pnc-20220331_htm.xml'
    file_path_instance = Path(dir) / file_instance
    with open(file_path_instance, 'r') as f:
        file_htm_xml = f.read()

    inst_doc = instance_doc.Instance_Doc()
    df_combine = inst_doc.create_xbrl_dataframe(file_htm_xml)
    selection = df_combine[(df_combine['concept']==xbrl_rqmt['xbrl_concept']) 
                            & (df_combine['dimension']==xbrl_rqmt['dimension']) 
                            & (df_combine['value_context']==xbrl_rqmt['value_context'])
                            & (df_combine['start']==xbrl_rqmt['start'])
                            & (pd.isna(df_combine['end'])==True)
                            ]
    result = selection.to_dict('records')

    assert True == True