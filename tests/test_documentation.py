import pytest
from pathlib import Path
import time

import pandas as pd

from sec_edgar_extractor.documentation import Documentation



def test_load_document():
    doc = Documentation()
    doc.load_documents()
    recs = []
    recs.append( doc.xbrl_description.shape[0] )
    recs.append( doc.xbrl_reference_arcs.shape[0] )
    recs.append( doc.xbrl_codification.shape[0] )

    assert recs == [14587, 11205, 5462]