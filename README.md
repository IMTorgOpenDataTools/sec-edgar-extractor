# SEC EDGAR Extract

This module provides functionality to perform the following:

* create configuration from firm's 10-K/-Q Instance Document (`xxx_htm.xml`) and associated 8-K
* parse and load xbrl documentation from us-gaap taxonomy, `us-gaap-doc-2022.xml`, [sec site](https://www.sec.gov/info/edgar/edgartaxonomies.shtml)
* extract specific account topic values from filings:
  - 10-K/-Q, from instance document
  - 8-K, from html-formatted exhibit


## Earnings Extraction Workflow

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


## TODO

Aspects that need improvement:

* automated creation of configuration file
* Exception: 'NoneType' object is not iterable
* 10+sec execution: bac
* bac Loans
* confidence
* wksheet-2 definitions (website, gaap taxonomy .xml)


## Usage and Testing

Enable vscode development container to install packages using:

```
sudo apt-get update
sudo apt-get upgrade
```

Super user may be needed to install all packages.  Some dependencies require multiple external packages.  To prepare the environment, do the following:

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