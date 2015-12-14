#!/usr/bin/env python
# simple wxmplot example

from numpy import linspace, sin, cos, random

def test_import():
    success = False
    try:
        import wxmplot
        success = True
    except:
        pass
    assert(success)
