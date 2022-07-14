import pytest

import os
import shutil
from bs4 import BeautifulSoup

from sec_edgar_extractor.utils import (
    Config
)



config = Config()
config.load_config_account_info()

def test_load_config_account_info():
    report_date_qtr = '2021-Q3'
    report_date_str = '2021-10-01'
    assert len( config.get(report_date=report_date_qtr) ) == len( config.get(report_date=report_date_str, mode='firm_records') ) == 17

def test_load_config_mode_df():
    report_date = '2021-10-01'
    df_config = config.get(report_date=report_date, mode='df')
    assert df_config.shape[0] == 33