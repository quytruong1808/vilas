#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

#python tools
import os
import thread
from threading import Thread

#ListView
from kivy.uix.listview import ListView
from kivy.adapters.listadapter import ListAdapter

# import source
from parsePdb import Variable
from Utils import PdbFile
#global variable
ItemId = 0

#Kivy file
Builder.load_file(os.path.dirname(__file__)+"/LabpiReceptor.kv")

class ReceptorScreen(Screen):
    root_path = os.path.dirname(__file__)

    pymol = ObjectProperty(None)
    list_adapter_receptor = ObjectProperty(None)

    receptorList = ObjectProperty(None)
    recetor_lv = ListView()

    def __init__(self, *args, **kwargs):
        super(ReceptorScreen, self).__init__(*args, **kwargs)
        list_item_args_converter = lambda row_index, obj: {'root_path': obj.root_path, 'item_id': obj.item_id, 'text': obj.text, 'pdbFile': obj.pdbFile, 'list_id': obj.list_id, 'number_chain': obj.number_chain}

        self.list_adapter_receptor = ReceptorAdapter(data=[],
                            args_converter=list_item_args_converter,
                            template='GroupListItem')
        self.recetor_lv = ListView(adapter=self.list_adapter_receptor,
                                divider_height= 1,
                                id='receptor_lv')
        self.receptorList.add_widget(self.recetor_lv)

    def setupView(self):
        data = []
        global ItemId
        ItemId = 0
        pdbFiles = Variable.parsepdb.Receptors
        for pdbFile in pdbFiles:
            ItemId+=1

            filename = os.path.basename(pdbFile.file_path)
            chainname = os.path.splitext(filename)[0]
            # Find number of chain avarible for kivy height
            number_chain = 0
            for chain in pdbFile.chains:
                if(chain.is_selected and chain.chain_type != 'ligand'):
                    number_chain += 1
                    pymol_thread = Thread(target = self.pymol_spectrum, args = (chain, chainname, str(chain.resindices[0])+'-'+str(chain.resindices[1]), ))
                    pymol_thread.start()
                    pymol_thread.join()

            filename = os.path.basename(pdbFile.file_path)
            data.append(DataItem(root_path=self.root_path, item_id=ItemId, text=filename, pdbFile=pdbFile , list_id = 'receptor_lv', number_chain = number_chain))

        ligands = Variable.parsepdb.Ligands
        for ligand in ligands:
            filename = os.path.basename(ligand.file_path)
            chainname = os.path.splitext(filename)[0]
            
            chains = ligand.chains
            for chain in chains:
                print str(chain.chain_view)
                pymol_thread = Thread(target = self.pymol_hide, args = (chain, chainname, ))
                pymol_thread.start()
                pymol_thread.join()

        self.recetor_lv.adapter.data = data
        self.recetor_lv._trigger_reset_populate()

    def set_pymol(self, pym):
        self.pymol = pym
        self.list_adapter_receptor.set_data(self.pymol)

    def pymol_spectrum(self, chain, chainname, value):
        self.pymol.cmd.color('gray', str(chain.chain_view) + ' & ' + chainname) 
        self.pymol.cmd.spectrum('count', 'rainbow', str(chain.chain_view) + ' & ' + chainname +' & resi '+str(value))
    
    def pymol_hide(self, chain, chainname):
        self.pymol.cmd.hide('cartoon', str(chain.chain_view) + ' & ' + chainname)



#--------------------------------------------------------#
# ListView class
class ReceptorAdapter(ListAdapter):
    pymol = ObjectProperty(None)

    def set_data(self, pym):
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
        filename = os.path.basename(item.pdbFile.file_path)
        chainname = os.path.splitext(filename)[0]
        for chain in chains:
            if chain.is_selected == False or chain.chain_type == 'ligand': 
                continue
            itemCB = GroupCheckBox()
            itemCB.chainName.text = chain.chain_name
            itemCB.chainBox.id = item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id) + '-_-' + item.pdbFile.file_path
            itemCB.chainBox.bind(active = self.on_check_active)
            itemCB.chainBox.active = chain.is_selected

            itemCB.resdiueFrom.id = '0-_-' + item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id) + '-_-' + item.pdbFile.file_path
            itemCB.resdiueFrom.text = str(chain.resindices[0]) + '-' + str(chain.resindices[1])
            itemCB.resdiueFrom.multiline=False
            itemCB.resdiueFrom.bind(text=self.on_text_change)
            # itemCB.resdiueTo.id = '1-_-' + item.list_id + '-_-' + str(index) + '-_-' + str(chain.chain_id)
            # itemCB.resdiueTo.text = str(chain.resindices[1])
            # itemCB.resdiueTo.multiline=False
            # itemCB.resdiueTo.bind(text=self.on_text_change)

            view_instance.cbLayout.add_widget(itemCB)
        return view_instance

    def on_check_active(self, checkbox, value):
        list_id = checkbox.id.split('-_-')[0]
        index = int(checkbox.id.split('-_-')[1])
        chain_id = int(checkbox.id.split('-_-')[2])
        file_path = str(checkbox.id.split('-_-')[3])

        filename = os.path.basename(file_path)
        chainname = os.path.splitext(filename)[0]


        if(list_id == 'receptor_lv'):
            chain =  Variable.parsepdb.Receptors[index].chains[chain_id]
            chain.is_group = value   
            if value == True:
                thread.start_new_thread( self.pymol.cmd.show, ('cartoon', str(chain.chain_view) + ' & ' + chainname,) )
            else:
                thread.start_new_thread( self.pymol.cmd.hide, ('cartoon', str(chain.chain_view) + ' & ' + chainname,) )

    def on_text_change(self, instance, value):
        et_type = int(instance.id.split('-_-')[0])
        list_id = instance.id.split('-_-')[1]
        index = int(instance.id.split('-_-')[2])
        chain_id = int(instance.id.split('-_-')[3])
        file_path = str(instance.id.split('-_-')[4])

        filename = os.path.basename(file_path)
        chainname = os.path.splitext(filename)[0]

        if(list_id == 'receptor_lv' and int(value.split('-')[0]) < int(value.split('-')[1]) ):
            chain = Variable.parsepdb.Receptors[index].chains[chain_id]
            chain.resindices[0] = value.split('-')[0] 
            chain.resindices[1] = value.split('-')[1]   

            # Spectrum in pymol
            pymol_thread = Thread(target = self.pymol_spectrum, args = (chain, chainname, value, ))
            pymol_thread.start()
            pymol_thread.join()
    
    def pymol_spectrum(self, chain, chainname, value):
        self.pymol.cmd.color('gray', str(chain.chain_view) + ' & ' + chainname) 
        self.pymol.cmd.spectrum('count', 'rainbow', str(chain.chain_view) + ' & ' + chainname +' & resi '+str(value))

class DataItem(object):
    def __init__(self, root_path='', item_id=0, text='', pdbFile='', list_id='', number_chain=0):
        self.item_id = item_id
        self.root_path = root_path
        self.text = text
        self.pdbFile = pdbFile
        self.list_id = list_id
        self.number_chain = number_chain
    pass


class GroupCheckBox(BoxLayout):
    pass