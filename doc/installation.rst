====================================
Downloading and Installation
====================================

Prerequisites
~~~~~~~~~~~~~~~

The wxmplot package requires Python, wxPython, numpy, and matplotlib.  Some
of the example applications rely on the Image module as well.

With wxPython and the WX matplotlib backend supported well on Python 2.7,
but poorly for Python 3, little testing has been done with wxPhoenix or the
matplotlib WX backend.

Downloads
~~~~~~~~~~~~~

.. _github:   http://github.com/newwville/wxmplot
.. _PyPI:     http://pypi.python.org/pypi/wxmplot

The latest version is available from `PyPI`_ or `github`_, and the package
can be installed with::

   pip install wxmplot

Development Version
~~~~~~~~~~~~~~~~~~~~~~~~

To get the latest development version, use::

   git clone http://github.com/newville/wxmplot.git

Installation from Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wxmplot is a pure python module, so installation on all platforms can use the source kit::

   tar xvzf wxmplot-0.9.XX.tar.gz
   cd wxmplot-0.9.XX/
   python setup.py install

You can also install with ``pip install wxmplot``, or for Anaconda Python,
using ``conda install -c newville wxmplot``

License
~~~~~~~~~~~~~

The wxmplot code is distribution under the following license:

  Copyright (c) 2015 Matthew Newville, The University of Chicago

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
