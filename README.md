# SEC EDGAR Extract

Extract information from SEC EDGAR filings.

Given the Filing with multiple exhibit documents:

* determine if exhibit file is extractable
  - requirements: i) good html, ii) contains multiple tables, iii) contains account term
  - maybe typical exhibit number (99.1)
* select the table that contains account value and save table to file
  - use table within table_id
  - maybe convert all html and use consistent page number
* convert html to pdf: py3-wkhtmltopdf
* apply cv to pdf for df output: camelot-py
* get target value from df


## Functionality

Aspects that need improvement:

* find documents that contain information: `search_docs_for_terms()` => unique_docs
* find the correct table in the document:
  - use table_id, make useful modifications (style), then save table to .pdf 
  - configuration with repeatable .pdf page number
  - process to get table_lst / new_lst
* parse table: cv and rules to get df
* query table: get account value



## Usage and Testing

Some dependencies require multiple external packages.  To prepare the environment, do the following:

```
#py3-wkhtmltopdf
apt-get install xvfb
apt-get install xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic
apt-get install wkhtmltopdf
#camelot
pipenv install opencv-python
#uTidylib
apt-get install libtidy-dev
```

Use `pytest --collect-only` to check dependencies

Uses exhibits from WFC, here: https://www.sec.gov/ix?doc=/Archives/edgar/data/0000072971/000007297122000003/wfc-20220114.htm.  Exhibits 99.1, 99.2 contain parsable tables, but 99.3 contains only images of ppt slides.




## References

* [account titles](https://www.nasdaq.com/articles/list-account-titles-accounting-2015-09-17)