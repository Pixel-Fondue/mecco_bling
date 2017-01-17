# python

import lx, lxu

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
