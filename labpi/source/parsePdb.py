from prody import *

from source.Utils import Chain


class ParsePdb(object):
    #Read pdb file
    def __init__(self, Receptors = [], Ligands = []):
        self.Receptors = Receptors
        self.Ligands = Ligands

    def listChain(self, pdbFile):
        listProtein = []
        listLigand = []
        listChains = []
        input = parsePDB(pdbFile)

        #Check protein
        hierView = input.getHierView()
        chains = list(hierView)
        for y in range(0, len(chains)):
            chain = chains[y].select('protein')
            if chain is None: continue 
            #get hierview again
            chain = chain.getHierView()
            listProtein.append(list(chain)[0])

        #Check ligand
        ligandView = input.select('not water and not ion and hetero')
        if not ligandView is None:
            #Get ligand array name
            ligands = set(ligandView.getResnames())
            for y in range(0, len(ligands)):
                listLigand.append(ligandView.select('resname '+ligands.pop()))

        for x in range(0, len(listProtein) + len(listLigand)):
            if x < len(listProtein):
                chain_name = "{0:8s} - {1:10s}{2:4s}{3:9s}".format(str(listProtein[x]), "protein - ", str(listProtein[x].numResidues()), ' residues')
                resindices = [listProtein[x].RedidueEnd()[0], listProtein[x].RedidueEnd()[len(listProtein[x].RedidueEnd())-1] ]
                chain = Chain(chain_id = x, chain_type = 'protein', chain_name = chain_name, chain_view = listProtein[x], is_selected = True, resindices = resindices, is_group = True)
                
            else: 
                y = x - len(listProtein)
                chain_name = "{0:8s} - {1:10s}{2:4s}{3:9s}".format(str(listLigand[y].getResnames()[0]), "ligand  - ", str(listLigand[y].numAtoms()), ' atoms')
                chain = Chain(chain_id = x, chain_type = 'ligand', chain_name = chain_name, chain_view = listLigand[y], is_selected = True, listLigand = [], is_group = True)
            listChains.append(chain)
        return listChains

    pass


class Variable():
    parsepdb = ParsePdb()

    pass
  