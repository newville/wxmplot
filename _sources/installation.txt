====================================
Downloading and Installation
====================================

Prerequisites
~~~~~~~~~~~~~~~

The wxmplot package requires Python, wxPython, numpy, and matplotlib.  Some
of the example applications rely on the Image module as well.

Downloads
~~~~~~~~~~~~~

The latest version is available from PyPI or CARS (Univ of Chicago):

.. _wxmplot-0.9.6.tar.gz (CARS): http://cars9.uchicago.edu/software/python/wxmplot/src/wxmplot-0.9.6.tar.gz
.. _wxmplot-0.9.6.tar.gz (PyPI): http://pypi.python.org/packages/source/w/wxmplot/wxmplot-0.9.6.tar.gz
.. _wxmplot-0.9.6.zip    (CARS): http://cars9.uchicago.edu/software/python/wxmplot/src/wxmplot-0.9.6.zip
.. _wxmplot-0.9.6.zip    (PyPI): http://pypi.python.org/packages/source/w/wxmplot/wxmplot-0.9.6.zip

.. _wxmplot github repository:   http://github.com/newville/wxmplot
.. _Python Setup Tools:        http://pypi.python.org/pypi/setuptools

+----------------------+------------------+-------------------------------------------+
|  Download Option     | Python Versions  |  Location                                 |
+======================+==================+===========================================+
|  Source Kit          | 2.6, 2.7         | - `wxmplot-0.9.6.tar.gz (CARS)`_          |
|                      |                  | - `wxmplot-0.9.6.tar.gz (PyPI)`_          |
|                      |                  | - `wxmplot-0.9.6.zip    (CARS)`_          |
|                      |                  | - `wxmplot-0.9.6.zip    (PyPI)`_          |
+----------------------+------------------+-------------------------------------------+
|  Development Version |   all            |  use `wxmplot github repository`_         |
+----------------------+------------------+-------------------------------------------+

if you have `Python Setup Tools`_  installed, you can download and install
the package simply with::

   easy_install -U wxmplot

Development Version
~~~~~~~~~~~~~~~~~~~~~~~~

To get the latest development version, use::

   git clone http://github.com/newville/wxmplot.git


Installation
~~~~~~~~~~~~~~~~~

This is a pure python module, so installation fon all platforms can use the source kit::

   tar xvzf wxmplot-0.9.6.tar.gz  or unzip wxmplot-0.9.6.zip
   cd wxmplot-0.9.6/
   python setup.py install

License
~~~~~~~~~~~~~

The wxmplot code is distribution under the following license:

  Copyright (c) 2011 Matthew Newville, The University of Chicago

  Permission to use and redistribute the source code or binary forms of this
  software and its documentation, with or without modification is hereby
  granted provided that the above notice of copyright, these terms of use,
  and the disclaimer of warranty below appear in the source code and
  documentation, and that none of the names of The University of Chicago or
  the authors appear in advertising or endorsement of works derived from this
  software without specific prior written permission from all parties.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
  DEALINGS IN THIS SOFTWARE.


