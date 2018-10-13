====================================
Downloading and Installation
====================================

Prerequisites
~~~~~~~~~~~~~~~

The wxmplot package requires wxpython, matplotlib, numpy, and six.
Matplotlib version 2.0 or higher is strongly recommended, though older
versions may still work.

WxPython 4.0 or higher is also strongly recommended, as it allows wxmplot
to work with Python 2.7 and 3.5, 3.6, and later. At this writing, little
testing has been done with Python 3.7.  WxPython version 2.9 and 3 may also
continue to work, but only support Python 2.7.


Downloads
~~~~~~~~~~~~~

.. _github:   http://github.com/newwville/wxmplot
.. _PyPI:     http://pypi.python.org/pypi/wxmplot

The latest version is available from `PyPI`_ or `github`_, and the package
can be installed with::

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
