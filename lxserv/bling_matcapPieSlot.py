# # python
#
# import lx, bling, os, lxu
#
# CMD_NAME = "bling.matcapPieSlot"
#
# class CommandClass(bling.CommanderClass):
#     _commander_default_values = []
#     _pieMenus = [None] * 8
#
#     def commander_arguments(self):
#         return [
#             {
#                 'name': 'slot',
#                 'datatype': 'integer',
#                 'label': 'Slot',
#                 'values_list_type': 'popup',
#                 'values_list': range(1,9),
#                 'flags': []
#             }, {
#                 'name': 'matcap',
#                 'datatype': 'string',
#                 'label': 'Matcap',
#                 'values_list_type': 'popup',
#                 'values_list': bling.MatcapListPop,
#                 'flags': ['query']
#             }
#         ]
#
#     @classmethod
#     def set_pie(cls, index, value):
#         cls._pieMenus[index] = value
#
#     def commander_execute(self, msg, flags):
#         index = self.commander_arg_value(0)
#         value = self.commander_arg_value(1)
#
#         lx.eval('user.value bling_pie_slot_%s {%s}' % (index, value))
#
#         self.set_pie(index, value)
#
# lx.bless(CommandClass, CMD_NAME)
