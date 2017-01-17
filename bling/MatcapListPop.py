import lx, lxifc, glob, os, re
from var import *
from getTNImage import *
from imageCache import *

class MatcapListPop(lxifc.UIValueHints):

    _list = []
    _imagePaths = []
    imageCache = imageCache()
    _selected = ""

    def __init__(self):
        self._notifiers = [('select.event', 'item +vdlt')]

        if not self._list:
            self.getMatcapListPop()

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
    def getMatcapListPop(cls):
        kitPath = KIT_FOLDER

        cls._list = []
        cls._imagePaths = []
        if kitPath != None:

            if lx.eval("user.value bling_matcap_use_file_prefix ?"):
                images = glob.glob(os.path.join(matcap_folder(), "%s*" % lx.eval("user.value bling_matcap_file_prefix ?")))
            else:
                images = [os.path.join(matcap_folder(), element) for element in os.listdir(matcap_folder())]

            images = [image for image in images if
                      os.path.isfile(image) and re.search('([^\\s]+(\\.(?i)(jpg|png|psd|exr|tga))$)', image.lower())]

            if not os.path.isdir(TN_FOLDER):
                os.mkdir(TN_FOLDER)

            for image in images:
                baseName = os.path.basename(image)[:-4]
                cleanFileName = baseName.replace(lx.eval("user.value bling_matcap_file_prefix ?"), "")
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

        cls._list.append(LABEL_NONE)
        cls._list.append(LABEL_OPEN_FOLDER)
        cls._list.append(LABEL_UPDATE)
        cls._imagePaths.append(NONE)
        cls._imagePaths.append(OPEN_FOLDER)
        cls._imagePaths.append(UPDATE)

    @staticmethod
    def makeTN(image, Full_TN_Path):
        imgSrvc = lx.service.Image()
        tnObj = GetTNImage(TN_W, TN_H, image, A=0)
        imgSrvc.Save(tnObj, "%s.png" % Full_TN_Path, "PNG", None)
