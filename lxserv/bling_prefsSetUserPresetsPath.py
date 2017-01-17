#python

import lx, lxu, modo, tagger, traceback

class CommandClass(lxu.command.BasicCommand):

    def basic_Execute(self, msg, flags):
        target = modo.dialogs.dirBrowse(tagger.LABEL_CHOOSE_FOLDER)
        lx.eval('user.value bling_matcap_directory {%s}' % target)

lx.bless(CommandClass, "bling.prefsSetUserPresetsPath")
