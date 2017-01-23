# python

import lx, bling, os, lxu

CMD_NAME = "bling.matcapAdd"

class CommandClass(bling.CommanderClass):
    _commander_default_values = []
    _icon = None
    _imageCache = bling.imageCache()

    def commander_arguments(self):
        return [
            {
                'name': 'matcap',
                'datatype': 'string',
                'label': 'Matcap',
                'values_list_type': 'popup',
                'values_list': bling.MatcapListPop,
                'flags': ['query']
            }
        ]

    def cmd_IconImage(self, w, h):
        image_path = self.commander_arg_value(0)
        if image_path:
            TN = self._imageCache.GetImageTN(image_path)
            return TN

    def commander_execute(self, msg, flags):
        image = self.commander_arg_value(0)
        MatcapListPop = bling.MatcapListPop()

        scnSel = lxu.select.SceneSelection().current()
        scnSrv = lx.service.Scene()
        render = scnSel.ItemLookup('Render')

        if image == bling.NONE:
            lx.eval("bling.matcapRemove")
            MatcapListPop.setSelected()

        elif image == bling.OPEN_FOLDER:
            lx.eval('file.open {%s}' % bling.matcap_folder())

        elif image == bling.UPDATE:
            lx.eval("bling.matcapRemove")
            MatcapListPop.getMatcapListPop()
            image = MatcapListPop.getSelected()

        if os.path.isfile(image):
            lx.eval("bling.matcapRemove")
            MatcapListPop.setSelected(image)

            matCapObj = scnSel.ItemAdd(scnSrv.ItemTypeLookup('matcapShader'))
            matCapObj.SetName(lx.eval("user.value bling_matcap_item_name ?"))

            parentGraph = scnSel.GraphLookup('parent')
            itemGraph = lx.object.ItemGraph(parentGraph)
            childrenCount = itemGraph.RevCount(render)
            itemGraph.SetLink(matCapObj, -1, render, -1)

            lx.eval('clip.addStill {%s}' % image)
            lx.eval('item.channel videoStill$colorspace "nuke-default:sRGB"')
            lx.eval('select.item {%s} set' % matCapObj.Ident())
            imageName = os.path.basename(image)
            lx.eval('matcap.image {%s:videoStill001}' % imageName[:imageName.rfind('.')])

            chan = scnSel.Channels('edit', 0.0)
            chnWrite = lx.object.ChannelWrite(chan)

            for channel in (('glOnly', 1), ('gamma', 1.0)):
                idx = matCapObj.ChannelLookup(channel[0])

                if type(channel[1]) == int:
                    return chnWrite.Integer(matCapObj, idx, channel[1])
                elif type(channel[1]) == float:
                    return chnWrite.Double(matCapObj, idx, channel[1])

            try:
                # Since we currently can not target a GL window, we
                # are wrapping this in a try just in case there is no available
                # GL window, or we are focused on a UV window
                lx.eval('!!view3d.shadingStyle advgl')
            except:
                pass

lx.bless(CommandClass, CMD_NAME)
