import os
import os.path
from subprocess import check_output
from subprocess import call

class PdbFile(object):
    def __init__(self, file_path = '', chains = []):
        self.file_path = file_path
        self.chains = chains
   	pass

class Chain(object):
    def __init__(self, chain_id = 0, chain_type = '', chain_name = '', chain_view = '', is_selected = True, resindices = [], is_group = True):
        self.chain_id = chain_id
        self.chain_type = chain_type
        self.chain_name = chain_name
        self.chain_view = chain_view #Information about this chain in prody format
        self.is_selected = is_selected
        self.resindices = resindices
        self.is_group = is_group  #If this chain is a part of receptor group for pulling
    pass

class DataController(object):
    main_path = os.path.dirname(__file__)

    username = check_output('echo $USER',shell=True).split('\n')[0]
    root_path = '/home/'+username

    def __init__(self, *args, **kwargs):
        super(DataController, self).__init__(*args, **kwargs)
        setting_path = self.root_path + '/.labpi_setting.txt'
        if os.path.isfile(setting_path) == True:
            if self.getdata('config_auto ') == 'True':
                self.root_path = self.main_path
        pass



    def getdata(self, name):
        f = open(self.root_path+'/.labpi_setting.txt', "r")
        contents = f.readlines()
        f.close()
        if len(self.substring(name,contents)) > 0:
            return contents[self.substring(name,contents)[0]].split(' = ')[1].split('\n')[0]
        else: 
            return ''

    def setdata(self, name, value):
        f = open(self.root_path+'/.labpi_setting.txt', "r")
        contents = f.readlines()
        f.close()

        contents[self.substring(name,contents)[0]] = name + ' = ' + value + '\n'

        f = open(self.root_path+'/.labpi_setting.txt', "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()

    def substring(self, mystr, mylist): 
        return [i for i, val in enumerate(mylist) if mystr in val]

    def checkExist(self):
        #Check root path
        setting_path = '/home/'+self.username + '/.labpi_setting.txt'
        if os.path.isfile(setting_path) == False:
            call('cp '+self.main_path+'/data/labpi_setting.txt '+setting_path, shell=True)
            run_path = '/home/'+self.username + '/Documents/labpi-result'
            self.setdata('path ', run_path)
            
class CheckPoint(object):
    point = ''
    step = ''

    pass