# python

import lx

NONE = "none"
LABEL_NONE = "(none)"

OPEN_FOLDER = "openFolder"
LABEL_OPEN_FOLDER = "Open Matcaps Directory"

UPDATE = "updateImages"
LABEL_UPDATE = "Update List"

KIT_NAME = "mecco_bling"
KIT_FOLDER = lx.eval("query platformservice alias ? {kit_%s:}" % KIT_NAME)

def matcap_folder():
    matcap_folder = lx.eval("user.value bling_matcap_directory ?")
    matcap_folder = lx.eval("query platformservice alias ? {%s}" % matcap_folder)
    return matcap_folder

TN_FOLDER = "kit_%s:Resources/thumbs_cache" % KIT_NAME
TN_FOLDER = lx.eval("query platformservice alias ? {%s}" % TN_FOLDER)

ALPHA_MATTE = "kit_%s:Resources/alphaMatte.exr" % KIT_NAME
ALPHA_MATTE = lx.eval("query platformservice alias ? {%s}" % ALPHA_MATTE)

TN_W = 32
TN_H = 32
