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


## Installation and Testing

### Applications

Enable vscode development container to install packages using:

```
sudo apt-get update
sudo apt-get upgrade
```

Super user may be needed to install all packages.  Some dependencies require multiple external packages.  To prepare the environment, do the following:

```
#py3-wkhtmltopdf
sudo apt-get install xvfb
sudo apt-get install xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic
sudo apt-get install wkhtmltopdf
#camelot
pipenv install opencv-python
#uTidylib
sudo apt-get install libtidy-dev
```


### Configuration

Some key artifacts are necessary to run the extractor.

* Firm Account Info
  - located at `sec_edgar_extractor/config/Firm_Account_Info.csv`
  - mapping of account topic to financial table presentation title (each firm) and XBRL Label
  - manually created currently
  - will be deprecated for an automated creation - TODO
* US GAAP Taxonomy
  - located at: `sec_edgar_extractor/config/us-gaap-doc-2022.xml` (codification) and `sec_edgar_extractor/config/us-gaap-ref-2022.xml` (description)
  - provides for all labels and associated definitions
  - download from [url](https://www.sec.gov/info/edgar/edgartaxonomies.shtml) for Operating Companies, go to table row Taxonomy Packages: `https://xbrl.fasb.org/us-gaap/2022/us-gaap-2022.zip`
  - unzip the file and review the `elts/` directory



### Unit testing

Use `pytest --collect-only` to check dependencies

Uses exhibits from WFC, here: https://www.sec.gov/ix?doc=/Archives/edgar/data/0000072971/000007297122000003/wfc-20220114.htm.  Exhibits 99.1, 99.2 contain parsable tables, but 99.3 contains only images of ppt slides.




## References

* [account titles](https://www.nasdaq.com/articles/list-account-titles-accounting-2015-09-17)