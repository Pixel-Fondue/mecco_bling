#python

import lx, lxu, modo, traceback

class CommandClass(lxu.command.BasicCommand):

    def basic_Execute(self, msg, flags):
        target = modo.dialogs.dirBrowse("Choose Folder")
        lx.eval('user.value bling_matcap_directory {%s}' % target)

lx.bless(CommandClass, "bling.prefsSetUserPresetsPath")
