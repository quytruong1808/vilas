#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

# Load file
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

#python tools
import os

#ListView
from kivy.uix.listview import ListView
from kivy.adapters.listadapter import ListAdapter

#source
from parsePdb import ParsePdb
from parsePdb import Variable
from Utils import PdbFile
from Utils import Chain


#Kivy file
Builder.load_file(os.path.dirname(__file__)+"/LabpiLoad.kv")

# global Variable
ItemId = 0

class LoadScreen(Screen):
    root_path = os.path.dirname(__file__)

    boxlist_1 = ObjectProperty(None)
    boxlist_2 = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LoadScreen, self).__init__(*args, **kwargs)

        list_item_args_converter = lambda row_index, obj: {'root_path': obj.root_path, 'item_id': obj.item_id, 'text': obj.text, 'pdbFile': obj.pdbFile, 'remove_item': obj.remove_item, 'list_id': obj.list_id}

        list_adapter_receptor = LoadAdapter(data=[], 
                            args_converter=list_item_args_converter,
                            template='LoadListItem')
        pdb_list_1 = ListView(adapter=list_adapter_receptor, 
                            divider_height= 1,
                            id='pdb_list_1')
        self.boxlist_1.add_widget(pdb_list_1)

        list_adapter_ligand = LoadAdapter(data=[], 
                            args_converter=list_item_args_converter,
                            template='LoadListItem')
        pdb_list_2 = ListView(adapter=list_adapter_ligand, 
                            divider_height= 1,
                            id='pdb_list_2')
        self.boxlist_2.add_widget(pdb_list_2)

    def show_load_receptor(self):
        # self._popup.dismiss()
        content = LoadDialog(load=self.load_receptor, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_load_ligand(self):
        # self._popup.dismiss()
        content = LoadDialog(load=self.load_ligand, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self):
        self._popup.dismiss()

    def load_receptor(self, path, file_path):
        # Add item to listview
        widget = self.findWidget(self.boxlist_1, 'pdb_list_1')
        if(not widget is None):
            global ItemId
            dataItem = []

            for fl in file_path:
                filename = os.path.basename(fl)
                if(os.path.splitext(filename)[1].split('.')[1]=='pdb'):     
                    ItemId += 1
                    #Add pdb file and chains to variable
                    chains = ParsePdb().listChain(fl)
                    pdbFile = PdbFile(file_path = fl, chains = chains)
                    Variable.parsepdb.Receptors.append(pdbFile)

                    dataItem.append(DataItem(root_path=self.root_path, item_id=ItemId, text=filename, pdbFile=pdbFile , remove_item=self.remove_item, list_id = 'pdb_list_1'))
                
            # print parsepdb.Receptors
            widget.adapter.data.extend(dataItem)
            widget._trigger_reset_populate()

            print len(Variable.parsepdb.Receptors)

        self.dismiss_popup()

    def load_ligand(self, path, file_path):
        # Add item to listview
        widget = self.findWidget(self.boxlist_2, 'pdb_list_2')
        if(not widget is None):
            global ItemId
            dataItem = []

            for fl in file_path:
                filename = os.path.basename(fl)
                if(os.path.splitext(filename)[1].split('.')[1]=='pdb'):     
                    ItemId += 1
                    #Add pdb file and chains to variable
                    chains = ParsePdb().listChain(fl)
                    pdbFile = PdbFile(file_path = fl, chains = chains)
                    Variable.parsepdb.Ligands.append(pdbFile)

                    dataItem.append(DataItem(root_path=self.root_path, item_id=ItemId, text=filename, pdbFile=pdbFile, remove_item=self.remove_item, list_id = 'pdb_list_2'))            

            # print parsepdb.Receptors
            widget.adapter.data.extend(dataItem)
            widget._trigger_reset_populate()

        self.dismiss_popup()
    
    # Listview
    def remove_item(self, item_id, list_id, pdbFile):
        widget = self.findWidget(self.boxlist_1, list_id)
        if(not widget is None):
            for dataItem in widget.adapter.data:
                if dataItem.item_id == item_id:
                    print 'File '+str(dataItem.text)+' was removed!'
                    widget.adapter.data.remove(dataItem)
                    widget._trigger_reset_populate()

                    #Xoa trong parsePDB
                    if(list_id == 'pdb_list_1'):
                        Variable.parsepdb.Receptors.remove(pdbFile)
                    else:
                        Variable.parsepdb.Ligands.remove(pdbFile)

                    break

    def findWidget(self, layout, widget_id):
        for widget in layout.walk():
            if(widget.id == widget_id):
                return widget
        return None

    pass

#--------------------------------------------------------#
# ListView class
class LoadAdapter(ListAdapter):

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
            itemCB = ItemCheckBox()
            itemCB.chainName.text = chain.chain_name
            itemCB.chainBox.id = item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id)
            itemCB.chainBox.bind(active = self.on_check_active)
            itemCB.chainBox.active = chain.is_selected
            view_instance.cbLayout.add_widget(itemCB)
        return view_instance

    def on_check_active(self, checkbox, value):
        list_id = checkbox.id.split('-_-')[0]
        index = int(checkbox.id.split('-_-')[1])
        chain_id = int(checkbox.id.split('-_-')[2])

        if(list_id == 'pdb_list_1'):
            Variable.parsepdb.Receptors[index].chains[chain_id].is_selected = value   
        else:
            Variable.parsepdb.Ligands[index].chains[chain_id].is_selected = value
        

    pass



class DataItem(object):
    def __init__(self, root_path = '', item_id=0, text='', pdbFile='', remove_item = ObjectProperty(None), list_id = ''):
        self.item_id = item_id
        self.text = text
        self.remove_item = remove_item
        self.pdbFile = pdbFile
        self.list_id = list_id
        self.root_path = root_path

class ItemCheckBox(BoxLayout):
    pass

#--------------------------------------------------------#
# Dialog class
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)