#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

#python tools
import os

#ListView
from kivy.uix.listview import ListView
from kivy.adapters.listadapter import ListAdapter

# import source
from source.parsePdb import Variable
from source.Utils import PdbFile
#global variable
ItemId = 0

class ReceptorScreen(Screen):
    receptorList = ObjectProperty(None)
    recetor_lv = ListView()

    def __init__(self, *args, **kwargs):
        super(ReceptorScreen, self).__init__(*args, **kwargs)
        list_item_args_converter = lambda row_index, obj: {'item_id': obj.item_id, 'text': obj.text, 'pdbFile': obj.pdbFile, 'list_id': obj.list_id, 'number_chain': obj.number_chain}

        list_adapter_receptor = ReceptorAdapter(data=[],
                            args_converter=list_item_args_converter,
                            template='GroupListItem')
        self.recetor_lv = ListView(adapter=list_adapter_receptor,
                                divider_height= 1,
                                id='receptor_lv')
        self.receptorList.add_widget(self.recetor_lv)

    def setupView(self):
        print "Receptor screen"
        print Variable.parsepdb.Receptors

        data = []
        global ItemId
        ItemId = 0
        pdbFiles = Variable.parsepdb.Receptors
        for pdbFile in pdbFiles:
            ItemId+=1

            # Find number of chain avarible
            number_chain = 0
            for chain in pdbFile.chains:
                if(chain.is_selected):
                    number_chain += 1

            filename = os.path.basename(pdbFile.file_path)
            data.append(DataItem(item_id=ItemId, text=filename, pdbFile=pdbFile , list_id = 'receptor_lv', number_chain = number_chain))

        self.recetor_lv.adapter.data = data
        self.recetor_lv._trigger_reset_populate()
    pass


#--------------------------------------------------------#
# ListView class
class ReceptorAdapter(ListAdapter):

    def create_view(self, index):
        item = self.get_data_item(index)
        if item is None:
            return None

        item_args = self.args_converter(index, item)

        item_args['index'] = index

        cls = self.get_cls()
        if cls:
            view_instance = cls(**item_args)
        else:
            view_instance = Builder.template(self.template, **item_args)

        if self.propagate_selection_to_data:
            if isinstance(item, SelectableDataItem):
                if item.is_selected:
                    self.handle_selection(view_instance)
            elif type(item) == dict and 'is_selected' in item:
                if item['is_selected']:
                    self.handle_selection(view_instance)
            elif hasattr(item, 'is_selected'):
                if (inspect.isfunction(item.is_selected)
                        or inspect.ismethod(item.is_selected)):
                    if item.is_selected():
                        self.handle_selection(view_instance)
                else:
                    if item.is_selected:
                        self.handle_selection(view_instance)
            else:
                msg = "ListAdapter: unselectable data item for {0}"
                raise Exception(msg.format(index))
        view_instance.bind(on_release=self.handle_selection)

        for child in view_instance.children:
            child.bind(on_release=self.handle_selection)

        # Set checkbox
        chains = item.pdbFile.chains
        for chain in chains:
            if chain.is_selected == False or chain.chain_type == 'ligand': 
                continue
            itemCB = GroupCheckBox()
            itemCB.chainName.text = chain.chain_name
            itemCB.chainBox.id = item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id)
            itemCB.chainBox.bind(active = self.on_check_active)
            itemCB.chainBox.active = chain.is_selected

            itemCB.resdiueFrom.id = '0-_-' + item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id)
            itemCB.resdiueFrom.text = str(chain.resindices[0])
            itemCB.resdiueFrom.multiline=False
            itemCB.resdiueFrom.bind(text=self.on_text_change)
            itemCB.resdiueFrom.id = '1-_-' + item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id)
            itemCB.resdiueTo.text = str(chain.resindices[1])
            itemCB.resdiueTo.multiline=False
            itemCB.resdiueTo.bind(text=self.on_text_change)

            view_instance.cbLayout.add_widget(itemCB)
        return view_instance

    def on_check_active(self, checkbox, value):
        list_id = checkbox.id.split('-_-')[0]
        index = int(checkbox.id.split('-_-')[1])
        chain_id = int(checkbox.id.split('-_-')[2])

        if(list_id == 'receptor_lv'):
            Variable.parsepdb.Receptors[index].chains[chain_id].is_group = value   

    def on_text_change(self, instance, value):
        et_type = int(instance.id.split('-_-')[0])
        list_id = checkbox.id.split('-_-')[1]
        index = int(checkbox.id.split('-_-')[2])
        chain_id = int(checkbox.id.split('-_-')[3])

        if(list_id == 'receptor_lv'):
            Variable.parsepdb.Receptors[index].chains[chain_id].group[et_type] = value   

        print value

    pass

class DataItem(object):
    def __init__(self, item_id=0, text='', pdbFile='', list_id='', number_chain=0):
        self.item_id = item_id
        self.text = text
        self.pdbFile = pdbFile
        self.list_id = list_id
        self.number_chain = number_chain
    pass


class GroupCheckBox(BoxLayout):
    pass