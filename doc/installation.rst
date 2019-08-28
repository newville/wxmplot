====================================
Downloading and Installation
====================================

Prerequisites
~~~~~~~~~~~~~~~

The current version of wxmplot is |release|, released in August, 2019.

The wxmplot package requires wxPython, matplotlib, numpy, and six.  All of
these are readily available from `pip` or on `conda` channels.

This is the final version to support Python 2.7 and WxPython below
version 4.  WxPython 4.0 is strongly recommended, and is required for
Python 3.5 and higher.  WxPython version 2.9 and 3 may also continue to
work with Python 2.7, and this combination is no longer tested.  Matplotlib
version 3.0 or higher is also strongly recommended. Older versions may
still work but are not tested.


Downloads
~~~~~~~~~~~~~

.. _github:   http://github.com/newwville/wxmplot
.. _PyPI:     http://pypi.python.org/pypi/wxmplot

The latest version (|release|) is available from `PyPI`_ or `github`_, and
the package can be installed with::

   pip install wxmplot

Users of anaconda python can also install wxmplot with::

   conda install -c gsecars wxmplot


Development Version
~~~~~~~~~~~~~~~~~~~~~~~~

To get the latest development version, use::

   git clone http://github.com/newville/wxmplot.git

Installation from Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wxmplot is a pure python module, so installation on all platforms can use
the source kit and a standard installation using::

   python setup.py install


License
~~~~~~~~~~~~~

The wxmplot code is distribution under the following license:

..  literalinclude:: ../LICENSE
