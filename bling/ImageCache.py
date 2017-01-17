# python

import lx

class imageCache():
    imageCache = {}

    def addImage(self, image, TN):
        if not self.imageCache.has_key(image):
            #lx.out('++ Adding Image: %s' % image)
            imgSrvc = lx.service.Image()
            im = imgSrvc.Load(TN)
            self.imageCache[image] = im

    def removeImage(self, image):
        if self.imageCache.has_key(image):
            #lx.out('-- Removing Image: %s' % image)
            del self.imageCache[image]

    def GetImageTN(self, image):
        if self.imageCache.has_key(image):
            return self.imageCache[image]
        else:
            return
