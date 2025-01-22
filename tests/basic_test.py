#!/usr/bin/env python
# simple wxmplot import

import numpy
import matplotlib

def test_import():
    import wxmplot
    success = True

    assert(success)


def test_interactive_import():
    import wxmplot.interactive as wi
    success = True
    assert(success)
