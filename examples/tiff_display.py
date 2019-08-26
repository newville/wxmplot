from os import path
from tifffile import imread

from wxmplot.interactive import imshow

thisdir, _ = path.split(__file__)
imgdata =  imread(path.join(thisdir, 'ceo2.tiff'))

imshow(imgdata, contrast_level=0.1, colormap='coolwarm')
