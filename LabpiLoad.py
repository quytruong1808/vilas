#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

# Load file
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

#python tools
import os

#ListView
from kivy.uix.listview import ListView
from kivy.adapters.listadapter import ListAdapter


# global variable
ItemId = 0

class LoadScreen(Screen):
    boxlist_1 = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LoadScreen, self).__init__(*args, **kwargs)

        list_item_args_converter = lambda row_index, obj: {'item_id': obj.item_id, 'text': obj.text, 'remove_item': obj.remove_item}

        list_adapter = LoadAdapter(data=[], 
                            args_converter=list_item_args_converter,
                            template='CustomListItem')
        pdb_list = ListView(adapter=list_adapter, 
                            id='pdb_list_1')
        self.boxlist_1.add_widget(pdb_list)

    def show_load(self):
        # self._popup.dismiss()
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self):
        self._popup.dismiss()

    def load(self, path, filename):
        widget = self.findWidget(self.boxlist_1, 'pdb_list_1')
        if(not widget is None):
            global ItemId
            ItemId += 1
            widget.adapter.data.extend([DataItem(item_id=ItemId, text=os.path.join(path, filename[0]), remove_item=self.remove_item)])
            widget._trigger_reset_populate()

        self.dismiss_popup()
    
    # Listview
    def remove_item(self, item_id):
        widget = self.findWidget(self.boxlist_1, 'pdb_list_1')
        if(not widget is None):
            for dataItem in widget.adapter.data:
                if dataItem.item_id == item_id:
                    print 'File '+str(dataItem.text)+' was removed!'
                    widget.adapter.data.remove(dataItem)
                    widget._trigger_reset_populate()
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
    
    pass



class DataItem(object):
    def __init__(self, item_id=0, text='', remove_item = ObjectProperty(None)):
        self.item_id = item_id
        self.text = text
        self.remove_item = remove_item

#--------------------------------------------------------#
# Dialog class
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)