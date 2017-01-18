# python

import lx
from var import *

def GetTNImage(w, h, path=None, R=255.0, G=255.0, B=255.0, A=255.0):
    imgSrvc = lx.service.Image()
    im = imgSrvc.Create(w, h, lx.symbol.iIMP_RGB24, 0)
    alphaMatte = imgSrvc.Create(w, h, lx.symbol.iIMP_RGB24, 0)
    output_image = imgSrvc.Create(w, h, lx.symbol.iIMP_RGBA32, 0)

    iout = lx.object.ImageWrite(output_image)

    # initialize blank image
    px_store = lx.object.storage()
    px_store.setType('b')
    px_store.setSize(w * 4)

    for line_number in range(h):
        px_store.set((R, G, B, A) * w)
        iout.SetLine(line_number, lx.symbol.iIMP_RGBA32, px_store)

    # open and resample target image
    if path != None:
        imLOAD = imgSrvc.Load(path)
        imgSrvc.Resample(im, imLOAD, 0)

    # load the alpha matte
    alphaMatte = imgSrvc.Load(ALPHA_MATTE)

    # apply the alpha matte line by line
    for line_number in range(h):

        im.GetLine(line_number, lx.symbol.iIMP_RGBA32, px_store)
        im_pixels_list = list(px_store.get())

        alphaMatte.GetLine(line_number, lx.symbol.iIMP_RGBA32, px_store)
        alpha_pixels_list = px_store.get()

        # im_pixels_list and alpha_pixels_list are 128 slots long: (R, G, B, A, R, G, B, A... etc)
        # so every 4 slots in the list is another RGBA vector (i.e. pixel)
        for index in range(w):
            # index*4+3 finds the pixel (index*4) and grabs its alpha value (+3)
            alpha_index = index*4+3
            im_pixels_list[alpha_index] = alpha_pixels_list[alpha_index]

        px_store.set(im_pixels_list)
        iout.SetLine(line_number, lx.symbol.iIMP_RGBA32, px_store)

    return output_image
