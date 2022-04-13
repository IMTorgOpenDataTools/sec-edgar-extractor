import pytest

import os
from pathlib import Path
import shutil
import json
from bs4 import BeautifulSoup

from sec_edgar_extractor.extract import Doc, Extractor





def test_extract_process():
    path_loc = Path('./tests/data/press_release')
    files = path_loc / 'files.json'

    with open(files, 'r') as f:
        string = f.read()
        data = json.loads(string)
    
    ex = Extractor()
    result = {}
    for k in data.keys():
        html_file = data[k]['input_file']
        desc = data[k]['input_desc']
        output = data[k]['output']

        loc = path_loc / html_file
        doc = Doc(Description=desc, FS_Location=loc)
        rec = ex.execute_extract_process(doc=doc, ticker=k)
        print(rec)
        result[k] = rec == output

    print(result)
    #summary = {k:v for k,v in result.items() if v == True}
    #assert len(summary) == len(result)
    assert True == False