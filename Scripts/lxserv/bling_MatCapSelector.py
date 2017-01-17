# python

import lx
import lxifc
import lxu
import os
import re
import glob
import traceback
import time

KIT_NAME = "mecco_bling"
KIT_FOLDER = lx.eval("query platformservice alias ? {kit_%s:}" % KIT_NAME)

MATCAP_FOLDER = lx.eval("user.value bling_matcap_directory ?")
MATCAP_FOLDER = lx.eval("query platformservice alias ? {%s}" % MATCAP_FOLDER)

TN_FOLDER = "kit_%s:Resources/thumbs_cache" % KIT_NAME
TN_FOLDER = lx.eval("query platformservice alias ? {%s}" % TN_FOLDER)

MATCAP_PREFIX = lx.eval("user.value bling_matcap_file_prefix ?")

MATCAP_NAME = lx.eval("user.value bling_matcap_item_name ?")

ALPHA_MATTE = "kit_%s:Resources/alphaMatte.exr" % KIT_NAME
ALPHA_MATTE = lx.eval("query platformservice alias ? {%s}" % ALPHA_MATTE)

TN_W = 32
TN_H = 32


def getMatcapImage(matcapName):
    scene_svc = lx.service.Scene()
    scene = lxu.select.SceneSelection().current()
    shadeloc_graph = lx.object.ItemGraph(scene.GraphLookup(lx.symbol.sGRAPH_SHADELOC))
    matcap_item = scene.ItemLookup(matcapName)

    for x in range(shadeloc_graph.FwdCount(matcap_item)):
        next_item = shadeloc_graph.FwdByIndex(matcap_item, x)
        if next_item.Type():
            next_item_type = next_item.Type()
            if next_item_type == scene_svc.ItemTypeLookup(lx.symbol.sITYPE_VIDEOSTILL):
                return scene.ItemLookup(next_item.Ident())

    return False


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


class CJ_MatcapList(lxifc.UIValueHints):

    _list = []
    _imagePaths = []
    imageCache = imageCache()
    _selected = ""

    def __init__(self):
        self._notifiers = [('select.event', 'item +vdlt')]

        if not self._list:
            self.getMatcapList()

    def uiv_Flags(self):
        return lx.symbol.fVALHINT_POPUPS

    def uiv_PopCount(self):
        return len(self._list)

    def uiv_PopUserName(self, index):
        return self._list[index].replace("_", " ")

    def uiv_PopInternalName(self, index):
        return self._imagePaths[index]

    def uiv_PopIconSize(self):
        return (TN_W, TN_W, TN_H)

    def uiv_PopFlags(self,index):
        if self._imagePaths[index] == self._selected:
            return lx.symbol.fPOPFLAGS_SELECTED
        else:
            return 0

    def uiv_PopIconImage(self, index):
        return self.imageCache.GetImageTN(self._imagePaths[index])

    def uiv_NotifierCount(self):
        return len(self._notifiers)

    def uiv_NotifierByIndex(self, index):
        return self._notifiers[index]

    @classmethod
    def setSelected(cls,val=""):
        cls._selected = val

    @classmethod
    def getSelected(cls):
        return cls._selected

    @classmethod
    def getMatcapList(cls):
        kitPath = KIT_FOLDER

        cls._list = []
        cls._imagePaths = []
        if kitPath != None:
            images = glob.glob(os.path.join(MATCAP_FOLDER, "%s*" % MATCAP_PREFIX))

            # Adam's hack to make sure we're only getting image files
            images = [image for image in images if
                      os.path.isfile(image) and re.search('([^\\s]+(\\.(?i)(jpg|png|psd|exr|tga))$)', image.lower())]

            if not os.path.isdir(TN_FOLDER):
                os.mkdir(TN_FOLDER)

            for image in images:
                baseName = os.path.basename(image)[:-4]
                cleanFileName = baseName.replace(MATCAP_PREFIX, "")
                modTime = os.path.getmtime(image)
                TN_Name = "%s_%s_%s" % (modTime, baseName, TN_W)

                Full_TN_Search_Path = os.path.join(TN_FOLDER, "*_%s_%s*" % (baseName, TN_W))
                Full_TN_Path = os.path.join(TN_FOLDER, TN_Name)

                Existing_TN = glob.glob(Full_TN_Search_Path)

                if len(Existing_TN) > 0:
                    #check out mod times
                    tnMod = float(os.path.basename(Existing_TN[0]).split('_')[0])
                    if modTime > tnMod:
                        os.remove(Existing_TN[0])
                        cls.imageCache.removeImage(image)
                        cls.makeTN(image, Full_TN_Path)

                    else:
                        Full_TN_Path = Existing_TN[0][:-4]
                else:
                    cls.makeTN(image, Full_TN_Path)

                cls._imagePaths.append(image)
                cls._list.append(cleanFileName)

                cls.imageCache.addImage(image, "%s.png" % Full_TN_Path)

        cls._list.append('(none)')
        cls._list.append('Open Matcaps Folder')
        cls._list.append('Update Images')
        cls._imagePaths.append('(none)')
        cls._imagePaths.append('openFolder')
        cls._imagePaths.append('updateImages')

    @staticmethod
    def makeTN(image, Full_TN_Path):
        imgSrvc = lx.service.Image()
        tnObj = GetTNImage(TN_W, TN_H, image, A=0)
        imgSrvc.Save(tnObj, "%s.png" % Full_TN_Path, "PNG", None)


class mecco_cmd_bling(lxu.command.BasicCommand):
    def __init__(self):

        lxu.command.BasicCommand.__init__(self)
        self.dyna_Add('image', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(0, lx.symbol.fCMDARG_QUERY)

    def arg_UIValueHints(self, index):
        return CJ_MatcapList()

    def basic_ButtonName(self):
        return "Matcap"

    def basic_Execute(self, msg, flags):
        try:
            self.CMD_EXE(msg, flags)
        except Exception:
            msg.SetCode(lx.result.FAILED)
            msg.SetMessage('common', None, 99)
            msg.SetArgumentString(1,traceback.format_exc())

    def CMD_EXE(self, msg, flags):

        image = self.dyna_String(0, "(none)")
        scnSel = lxu.select.SceneSelection().current()
        render = self.lookUP('Render')
        scnSrv = lx.service.Scene()
        matCapList = CJ_MatcapList()

        if image == "(none)":
            self.removeMatCap()
            matCapList.setSelected()

        elif image == "openFolder":
            lx.eval('file.open {%s}' % MATCAP_FOLDER)

        elif image == "updateImages":
            self.removeMatCap()
            matCapList.getMatcapList()
            image = matCapList.getSelected()

        if os.path.isfile(image):
            self.removeMatCap()
            matCapList.setSelected(image)

            matCapObj = scnSel.ItemAdd(scnSrv.ItemTypeLookup('matcapShader'))
            matCapObj.SetName(MATCAP_NAME)

            parentGraph = scnSel.GraphLookup('parent')
            itemGraph = lx.object.ItemGraph(parentGraph)
            childrenCount = itemGraph.RevCount(render)
            itemGraph.SetLink(matCapObj, -1, render, -1)

            lx.eval('clip.addStill {%s}' % image)
            lx.eval('item.channel videoStill$colorspace "nuke-default:sRGB"')
            lx.eval('select.item {%s} set' % matCapObj.Ident())
            imageName = os.path.basename(image)
            lx.eval('matcap.image {%s:videoStill001}' % imageName[:imageName.rfind('.')])

            self.writeChannel(matCapObj, 'glOnly', 1)
            self.writeChannel(matCapObj, 'gamma', 1.0)

            try:
                # Since we currently can not target a GL window, we
                # are wrapping this in a try just in case there is no available
                # GL window, or we are focused on a UV window
                lx.eval('!!view3d.shadingStyle advgl')
            except:
                pass

    def removeMatCap(self):
        scnSel = lxu.select.SceneSelection().current()
        existingMatCap = self.lookUP(MATCAP_NAME)
        if existingMatCap != None:
            scnSel.ItemRemove(getMatcapImage(MATCAP_NAME))
            scnSel.ItemRemove(existingMatCap)

    def cmd_Query(self, index, vaQuery):
        pass

    def lookUP(self, itemName):

        scnSel = lxu.select.SceneSelection().current()

        try:
            itemObj = scnSel.ItemLookup(itemName)
        except:
            return None

        return itemObj

    def writeChannel(self, item, channelName, value, actionLayer='edit', valType=None):
        scnSel = lxu.select.SceneSelection().current()
        chan = scnSel.Channels(actionLayer, 0.0)
        chnWrite = lx.object.ChannelWrite(chan)

        try:
            idx = item.ChannelLookup(channelName)

            if valType == None:
                valType = type(value)

            if valType == str:
                return chnWrite.String(item, idx, str(value))
            elif valType == int:
                return chnWrite.Integer(item, idx, int(value))
            elif valType == float:
                return chnWrite.Double(item, idx, float(value))
        except Exception, e:
            #lx.out('%s - %s : %s' % (channelName,value,traceback.format_exc()))
            return "Error"

    def basic_Enable(self, msg):
        return True

lx.bless(mecco_cmd_bling, "mecco.bling")
