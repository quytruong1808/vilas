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


class LoadScreen(Screen):
    boxlist_1 = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LoadScreen, self).__init__(*args, **kwargs)

        list_adapter = LoadAdapter(data=[], template='CustomListItem')
        pdb_list = ListView(adapter=list_adapter, id='pdb_list_1')
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
        for widget in self.boxlist_1.walk():
            if(widget.id == 'pdb_list_1'):
                widget.adapter.data.extend([os.path.join(path, filename[0])])
                widget._trigger_reset_populate()


        self.dismiss_popup()
    pass

#--------------------------------------------------------#
# Adapter class
class LoadAdapter(ListAdapter):
    def remove_item(self):
        if self.selection:
            selection = self.selection[0].text
            self.data.remove(selection)
            # self.task_list._trigger_reset_populate()

    pass

#--------------------------------------------------------#
# Dialog class
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)