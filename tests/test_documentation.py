import pytest
from pathlib import Path
import time

import pandas as pd

from sec_edgar_extractor.documentation import Documentation
from sec_edgar_extractor.extract import Extractor






def test_load_document():
    doc = Documentation()
    doc.load_documents()

    recs = []
    recs.append( doc.xbrl_description.shape[0] )
    recs.append( doc.xbrl_reference_arcs.shape[0] )
    recs.append( doc.xbrl_codification.shape[0] )

    assert recs == [14587, 11205, 5462]


def test_create_documentation():
    doc = Documentation()
    doc.load_documents()
    ex = Extractor()

    df_config = ex.config.get(mode='df')
    xbrl_labels = set( df_config['xbrl'].tolist() )
    doc_records = doc.get_records(xbrl_labels)

    assert len(doc_records) == 19