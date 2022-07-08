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
    assert len( config.get() ) == len( config.get(mode='firm_records') ) == 17

def test_load_config_mode_df():
    df_config = config.get(mode='df')
    assert df_config.shape[0] == 33