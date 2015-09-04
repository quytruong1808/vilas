class PdbFile(object):
    def __init__(self, file_path = '', chains = []):
        self.file_path = file_path
        self.chains = chains
   	pass

class Chain(object):
    def __init__(self, chain_id = 0, chain_type = '', chain_name = '', is_selected = True, resindices = [], is_group = True):
        self.chain_id = chain_id
        self.chain_type = chain_type
        self.chain_name = chain_name
        self.is_selected = is_selected
        self.resindices = resindices
        self.is_group = is_group 
    pass

class DataController(object):
    def getdata(self, name):
        f = open('data/setting.txt', "r")
        contents = f.readlines()
        f.close()
        if len(self.substring(name,contents)) > 0:
            return contents[self.substring(name,contents)[0]].split(' = ')[1].split('\n')[0]
        else: 
            return ''

    def setdata(self, name, value):
        f = open('data/setting.txt', "r")
        contents = f.readlines()
        f.close()

        contents[self.substring(name,contents)[0]] = name + ' = ' + value + '\n'

        f = open('data/setting.txt', "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()

    def substring(self, mystr, mylist): 
        return [i for i, val in enumerate(mylist) if mystr in val]