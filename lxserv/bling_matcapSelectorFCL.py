# # python
#
# import lx, lxifc, lxu.command, modo, tagger, random
#
# CMD_NAME = "bling.matcapSelectorFCL"
#
#
# def list_commands():
#     fcl = []
#     return fcl
#
#
# class CommandClass(tagger.CommanderClass):
#     _commander_default_values = []
#
#     def commander_arguments(self):
#         return [
#                 {
#                     'name': tagger.QUERY,
#                     'label': tagger.LABEL_QUERY,
#                     'datatype': 'integer',
#                     'default': '',
#                     'values_list_type': 'fcl',
#                     'values_list': list_commands,
#                     'flags': ['query'],
#                 }
#             ]
#
#     def commander_notifiers(self):
#         return [("bling.notifier", "")]
#
#
# lx.bless(CommandClass, CMD_NAME)
