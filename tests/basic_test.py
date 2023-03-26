#!/usr/bin/env python
# simple wxmplot import

import numpy
import matplotlib

def test_import():
    success = False
    try:
        import wxmplot
        success = True
    except:
        pass
    assert(success)


def test_interactive_import():
    success = False
    try:
        import wxmplot.interactive as wi
        success = True
    except:
        pass
    assert(success)
