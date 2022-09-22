#!/usr/bin/env python
"""
   wxmplot: wxPython plotting widgets using matplotlib.

   wxmplot provides advanced wxPython widgets for plotting and image
   display based on matplotlib. The plotting and image display wx Panels
   and Frames it provides are easy for the programmer to include and work
   with from wx programs.  More importantly, the widgets created by wxmplot
   give the end user a flexible set of tools for interacting with their
   data and customizing the plots and displays.  wxmplot panels are more
   interactive than typical displayss from matplotlib's pyplot module.

   version: 0.9.49
   last update: 2022-Mar-20
   License:  MIT
   Author:  Matthew Newville <newville@cars.uchicago.edu>
            Center for Advanced Radiation Sources,
            The University of Chicago

   the main widgets provided by wxmplot are:

      PlotPanel: wx.Panel for basic 2-D line plots (roughly matplotlib `plot`)

      PlotFrame: wx.Frame containing a PlotPanel

      ImagePanel: wx.Panel for image display (roughly matplotlib `imshow`)

      ImageFrame: wx.Frame containing ImagePanel
"""
import sys
import wx

from .version import version as __version__
from .plotpanel import PlotPanel
from .imagepanel import ImagePanel

from .baseframe import BaseFrame
from .plotframe import PlotFrame


from .imageframe import ImageFrame
from .multiframe import MultiPlotFrame
from .stackedplotframe import StackedPlotFrame
from .residualplotframe import ResidualPlotFrame
from .imagematrixframe import ImageMatrixFrame
from .plotapp  import PlotApp
