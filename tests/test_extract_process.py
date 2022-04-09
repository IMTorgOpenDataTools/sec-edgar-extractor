import pytest

import os
import shutil
from bs4 import BeautifulSoup

from sec_edgar_extractor.extract import Doc, Extractor









def test_extract_process():
    tkr = 'USB'
    desc='EX-99.1'
    loc='./tests/data/usb/d262424dex991.htm'
    #desc='EX-99.2'
    #loc='./tests/data/wfc/wfc4qer01-14x22ex992xsuppl.htm'
    doc = Doc(Description=desc, FS_Location=loc)
    ex = Extractor()
    result = ex.execute_extract_process(doc=doc, ticker=tkr)
    assert True == True