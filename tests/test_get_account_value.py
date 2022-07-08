import pytest
import json

from sec_edgar_extractor.utils import (
    correct_row_list,
    take_val_from_column
)






def test_correct_row_list():
    file_path = './tests/data/tables/table_rows.json'
    with open(file_path, 'r') as f:
        string = f.read()
        data = json.loads(string)
    
    result = {}
    for k in data.keys():
        row = data[k]["input"]
        fixed_row = correct_row_list(row)
        test = fixed_row == data[k]["output"]
        result[k] = test
    outcome = {k:v for k,v in result.items() if v == True}
    assert len(outcome) == len(result)


def test_take_val_from_column():
    col = '<left-most>'
    row = [2058, 2265, 2262, 8578, 8936]
    val = take_val_from_column(row, col)
    assert val == 2058