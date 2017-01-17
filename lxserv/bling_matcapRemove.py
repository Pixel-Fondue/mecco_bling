# python

import lx, bling, os, lxu

CMD_NAME = "bling.matcapRemove"

class CommandClass(bling.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        scnSel = lxu.select.SceneSelection().current()

        try:
            existingMatCap = scnSel.ItemLookup(lx.eval("user.value bling_matcap_item_name ?"))
        except:
            return

        scnSel.ItemRemove(bling.getMatcapImage(lx.eval("user.value bling_matcap_item_name ?")))
        scnSel.ItemRemove(existingMatCap)

lx.bless(CommandClass, CMD_NAME)
