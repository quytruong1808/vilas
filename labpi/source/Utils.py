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