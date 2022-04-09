import pytest

import os
import shutil
from bs4 import BeautifulSoup

from sec_edgar_extractor.utils import (
    load_config_account_info
)







def test_load_config_account_info():
    config = load_config_account_info()
    assert len(config) == 9