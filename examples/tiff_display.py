from os import path
from tifffile import imread

from wxmplot.interactive import imshow, wxloop

thisdir, _ = path.split(__file__)
imgdata =  imread(path.join(thisdir, 'ceo2.tiff'))

imshow(imgdata, contrast_level=0.5, colormap='plasma')
wxloop()
