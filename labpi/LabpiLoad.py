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
from source.parsePdb import ParsePdb

# global variable
ItemId = 0
parsepdb = ParsePdb()

class LoadScreen(Screen):
    boxlist_1 = ObjectProperty(None)
    boxlist_2 = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LoadScreen, self).__init__(*args, **kwargs)

        list_item_args_converter = lambda row_index, obj: {'item_id': obj.item_id, 'text': obj.text, 'file_path': obj.file_path, 'remove_item': obj.remove_item, 'list_id': obj.list_id}

        list_adapter_receptor = LoadAdapter(data=[], 
                            args_converter=list_item_args_converter,
                            template='CustomListItem')
        pdb_list_1 = ListView(adapter=list_adapter_receptor, 
                            divider_height= 1,
                            id='pdb_list_1')
        self.boxlist_1.add_widget(pdb_list_1)

        list_adapter_ligand = LoadAdapter(data=[], 
                            args_converter=list_item_args_converter,
                            template='CustomListItem')
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
            global parsepdb
            dataItem = []

            for fl in file_path:
                filename = os.path.basename(fl)
                if(os.path.splitext(filename)[1].split('.')[1]=='pdb'):     
                    ItemId += 1
                    dataItem.append(DataItem(item_id=ItemId, text=filename, file_path=fl, remove_item=self.remove_item, list_id = 'pdb_list_1'))
                    parsepdb.Receptors.append(fl)

            # print parsepdb.Receptors
            widget.adapter.data.extend(dataItem)
            widget._trigger_reset_populate()

        self.dismiss_popup()

    def load_ligand(self, path, file_path):
        # Add item to listview
        widget = self.findWidget(self.boxlist_2, 'pdb_list_2')
        if(not widget is None):
            global ItemId
            global parsepdb
            dataItem = []

            for fl in file_path:
                filename = os.path.basename(fl)
                if(os.path.splitext(filename)[1].split('.')[1]=='pdb'):     
                    ItemId += 1
                    dataItem.append(DataItem(item_id=ItemId, text=filename, file_path=fl, remove_item=self.remove_item, list_id = 'pdb_list_2'))
                    parsepdb.Ligands.append(fl)

            # print parsepdb.Receptors
            widget.adapter.data.extend(dataItem)
            widget._trigger_reset_populate()

        self.dismiss_popup()
    
    # Listview
    def remove_item(self, item_id, list_id):
        widget = self.findWidget(self.boxlist_1, list_id)
        if(not widget is None):
            for dataItem in widget.adapter.data:
                if dataItem.item_id == item_id:
                    print 'File '+str(dataItem.text)+' was removed!'
                    widget.adapter.data.remove(dataItem)
                    widget._trigger_reset_populate()

                    #Xoa trong parsePDB
                    global parsepdb
                    parsepdb.Receptors.remove(dataItem.file_path)
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
        listChains = parsepdb.listChain(item.file_path)
        for chain in listChains:
            itemCB = ItemCheckBox()
            itemCB.chainName.text = str(chain)
            view_instance.cbLayout.add_widget(itemCB)
        return view_instance

    pass



class DataItem(object):
    def __init__(self, item_id=0, text='', file_path='', remove_item = ObjectProperty(None), list_id = ''):
        self.item_id = item_id
        self.text = text
        self.remove_item = remove_item
        self.file_path = file_path
        self.list_id = list_id

class ItemCheckBox(BoxLayout):
    pass

#--------------------------------------------------------#
# Dialog class
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)