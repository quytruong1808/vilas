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
from multiprocessing import Process
from threading import Thread
import thread
import time

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
loadPymol = False;

class LoadScreen(Screen):
    root_path = os.path.dirname(__file__)

    boxlist_1 = ObjectProperty(None)
    boxlist_2 = ObjectProperty(None)
    list_adapter_receptor = ObjectProperty(None)
    list_adapter_ligand = ObjectProperty(None)
    pymol = ObjectProperty(None)

    def setupView(self):
        receptors = Variable.parsepdb.Receptors
        for receptor in receptors:
            filename = os.path.basename(receptor.file_path)
            chainname = os.path.splitext(filename)[0]

            chains = receptor.chains
            for chain in chains:
                if chain.is_selected == True:
                    pymol_thread = Thread(target = self.pymol_show, args = (chain, chainname, ))
                    pymol_thread.start()

        ligands = Variable.parsepdb.Ligands
        for ligand in ligands:
            filename = os.path.basename(ligand.file_path)
            chainname = os.path.splitext(filename)[0]
            
            chains = ligand.chains
            for chain in chains:
                if chain.is_selected == True:
                    pymol_thread = Thread(target = self.pymol_show, args = (chain, chainname, ))
                    pymol_thread.start()

    def pymol_show(self, chain, chainname):
        for chain in chains:
            if chain.chain_type == 'protein':
                self.pymol.cmd.show_as('cartoon', str(chain.chain_view) + ' & ' + chainname)
                self.pymol.cmd.cartoon('automatic', str(chain.chain_view) + ' & ' + chainname)
            else:
                self.pymol.cmd.show_as('sticks', 'resname ' + str(chain.chain_view.getResnames()[0]) + ' & ' + chainname)

        self.pymol.util.cbc()

    def __init__(self, *args, **kwargs):
        super(LoadScreen, self).__init__(*args, **kwargs)

        list_item_args_converter = lambda row_index, obj: {'root_path': obj.root_path, 'item_id': obj.item_id, 'text': obj.text, 'pdbFile': obj.pdbFile, 'remove_item': obj.remove_item, 'zoom_item': obj.zoom_item, 'list_id': obj.list_id}

        self.list_adapter_receptor = LoadAdapter(data=[], 
                            args_converter=list_item_args_converter,
                            template='LoadListItem')
        pdb_list_1 = ListView(adapter=self.list_adapter_receptor, 
                            divider_height= 1,
                            id='pdb_list_1')
        self.boxlist_1.add_widget(pdb_list_1)

        self.list_adapter_ligand = LoadAdapter(data=[], 
                            args_converter=list_item_args_converter,
                            template='LoadListItem')
        pdb_list_2 = ListView(adapter=self.list_adapter_ligand, 
                            divider_height= 1,
                            id='pdb_list_2')
        self.boxlist_2.add_widget(pdb_list_2)

    def set_pymol(self, pym):
        self.pymol = pym
        self.list_adapter_receptor.setdata(pym)
        self.list_adapter_ligand.setdata(pym)

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
            global ItemId, loadPymol
            dataItem = []                

            for fl in file_path:
                filename = os.path.basename(fl)
                if(os.path.splitext(filename)[1].split('.')[1]=='pdb'):   
                    
                    ItemId += 1
                    #Add pdb file and chains to variable
                    chains = ParsePdb().listChain(fl)
                    pdbFile = PdbFile(file_path = fl, chains = chains)
                    Variable.parsepdb.Receptors.append(pdbFile)

                    dataItem.append(DataItem(root_path=self.root_path, item_id=ItemId, text=filename, pdbFile=pdbFile , remove_item=self.remove_item, zoom_item=self.zoom_item, list_id = 'pdb_list_1'))
                
                    #load pymol
                    pymol_thread = Thread(target = self.load_pymol, args = (chains, fl, ))
                    pymol_thread.start()

            widget.adapter.data.extend(dataItem)
            widget._trigger_reset_populate()

            print len(Variable.parsepdb.Receptors)

        self.dismiss_popup()

    def load_pymol(self, chains, fl):
        global loadPymol  
        if loadPymol == False:
            loadPymol = True
            self.pymol.finish_launching()

        filename = os.path.basename(fl)
        chainname = os.path.splitext(filename)[0]

        self.pymol.cmd.load(fl)
        self.pymol.cmd.zoom(chainname)
        for chain in chains:
            if chain.chain_type == 'protein':
                self.pymol.cmd.show_as('cartoon', str(chain.chain_view) + ' & ' + chainname)
                self.pymol.cmd.cartoon('automatic', str(chain.chain_view) + ' & ' + chainname)
            else:
                self.pymol.cmd.show_as('sticks', 'resname ' + str(chain.chain_view.getResnames()[0]) + ' & ' + chainname)
                # self.pymol.cmd('set stick_color red')
        self.pymol.util.cbc()
        # pymol.cmd.show_as('sticks', 'resn FDA')

    def load_ligand(self, path, file_path):
        # Add item to listview
        widget = self.findWidget(self.boxlist_2, 'pdb_list_2')
        if(not widget is None):
            global ItemId
            dataItem = []

            for fl in file_path:
                filename = os.path.basename(fl)
                if(os.path.splitext(filename)[1].split('.')[1]=='pdb'):     
                    # global loadPymol  
                    # if loadPymol == False:
                    #     loadPymol = True
                    #     thread.start_new_thread( self.pymol.finish_launching, ())

                    ItemId += 1
                    #Add pdb file and chains to variable
                    chains = ParsePdb().listChain(fl)
                    pdbFile = PdbFile(file_path = fl, chains = chains)
                    Variable.parsepdb.Ligands.append(pdbFile)

                    dataItem.append(DataItem(root_path=self.root_path, item_id=ItemId, text=filename, pdbFile=pdbFile, remove_item=self.remove_item, zoom_item=self.zoom_item, list_id = 'pdb_list_2'))            

                    #load pymol
                    pymol_thread = Thread(target = self.load_pymol, args = (chains, fl, ))
                    pymol_thread.start()
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

                    filename = os.path.basename(pdbFile.file_path)
                    chainname = os.path.splitext(filename)[0]
                    thread.start_new_thread( self.pymol.cmd.hide, ('cartoon', chainname,) )
                    thread.start_new_thread( self.pymol.cmd.hide, ('sticks',  chainname,) )

                    #Xoa trong parsePDB
                    if(list_id == 'pdb_list_1'):
                        Variable.parsepdb.Receptors.remove(pdbFile)
                    else:
                        Variable.parsepdb.Ligands.remove(pdbFile)

                    break

    def zoom_item(self, pdbFile):
        filename = os.path.basename(pdbFile.file_path)
        chainname = os.path.splitext(filename)[0]
        self.pymol.cmd.zoom(chainname)        

    def findWidget(self, layout, widget_id):
        for widget in layout.walk():
            if(widget.id == widget_id):
                return widget
        return None

    pass

#--------------------------------------------------------#
# ListView class
class LoadAdapter(ListAdapter):
    pymol = ObjectProperty(None)

    def setdata(self, pym):
        self.pymol = pym

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
            itemCB.chainBox.id = item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id) + '-_-' + item.pdbFile.file_path
            itemCB.chainBox.bind(active = self.on_check_active)
            itemCB.chainBox.active = chain.is_selected
            view_instance.cbLayout.add_widget(itemCB)
        return view_instance

    def on_check_active(self, checkbox, value):
        list_id = checkbox.id.split('-_-')[0]
        index = int(checkbox.id.split('-_-')[1])
        chain_id = int(checkbox.id.split('-_-')[2])
        file_path = str(checkbox.id.split('-_-')[3])

        filename = os.path.basename(file_path)
        chainname = os.path.splitext(filename)[0]

        if(list_id == 'pdb_list_1'):
            chain = Variable.parsepdb.Receptors[index].chains[chain_id]
            chain.is_selected = value   
            if value == True:
                if chain.chain_type == 'protein':
                    thread.start_new_thread( self.pymol.cmd.show, ('cartoon', str(chain.chain_view) + ' & ' + chainname,) )
                else: 
                    thread.start_new_thread( self.pymol.cmd.show, ('sticks', 'resname ' + str(chain.chain_view.getResnames()[0]) + ' & ' + chainname,) )
            else:
                if chain.chain_type == 'protein':
                    thread.start_new_thread( self.pymol.cmd.hide, ('cartoon', str(chain.chain_view) + ' & ' + chainname,) )
                else:
                    thread.start_new_thread( self.pymol.cmd.hide, ('sticks', 'resname ' + str(chain.chain_view.getResnames()[0]) + ' & ' + chainname,) )
        else:
            chain =  Variable.parsepdb.Ligands[index].chains[chain_id]
            chain.is_selected = value
            if value == True:
                if chain.chain_type == 'protein':
                    thread.start_new_thread( self.pymol.cmd.show, ('cartoon', str(chain.chain_view) + ' & ' + chainname,) )
                else:
                    thread.start_new_thread( self.pymol.cmd.show, ('sticks', 'resname ' + str(chain.chain_view.getResnames()[0]) + ' & ' + chainname,) )
            else:
                if chain.chain_type == 'protein':
                    thread.start_new_thread( self.pymol.cmd.hide, ('cartoon', str(chain.chain_view) + ' & ' + chainname,) )
                else:
                    thread.start_new_thread( self.pymol.cmd.hide, ('sticks', 'resname ' + str(chain.chain_view.getResnames()[0]) + ' & ' + chainname,) )
    pass



class DataItem(object):
    def __init__(self, root_path = '', item_id=0, text='', pdbFile='', remove_item = ObjectProperty(None), zoom_item = ObjectProperty(None), list_id = ''):
        self.item_id = item_id
        self.text = text
        self.remove_item = remove_item
        self.pdbFile = pdbFile
        self.list_id = list_id
        self.root_path = root_path
        self.zoom_item = zoom_item

class ItemCheckBox(BoxLayout):
    pass

#--------------------------------------------------------#
# Dialog class
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)