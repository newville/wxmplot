from os import path
from tifffile import imread

import wxmplot.interactive as wi

thisdir, _ = path.split(__file__)
imgdata =  imread(path.join(thisdir, 'ceo2.tiff'))

wi.imshow(imgdata, contrast_level=0.1, colormap='coolwarm')
