from prody import *
import os
import sys
labpi_path = os.path.dirname(__file__) + '/..'
sys.path.insert(0, labpi_path)

from Utils import Chain
ChainNames = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','P','Q','R','S','T','U','V','Y','Z']


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
            #get hierview again => change chain name if it null
            chain = chain.getHierView()
            if str(list(chain)[0]).replace(' ','') == 'Chain':
                for index in range(0, 22):
                    is_double = False
                    for protein in listProtein:
                        if 'Chain '+ChainNames[index] == str(protein):
                            is_double = True
                            break
                    if is_double == False:
                        list(chain)[0].setChids(ChainNames[index] )
                        writePDB(pdbFile, input)
                        break
                
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
                resindices = str(listProtein[x].getResnums()[0])+'-'+str(listProtein[x].getResnums()[len(listProtein[x].getResnums())-1])
                chain = Chain(chain_id = x, chain_type = 'protein', chain_name = chain_name, chain_view = listProtein[x], is_selected = True, resindices = resindices, is_group = True)
                
            else: 
                y = x - len(listProtein)
                chain_name = "{0:8s} - {1:10s}{2:4s}{3:9s}".format(str(listLigand[y].getResnames()[0]), "ligand  - ", str(listLigand[y].numAtoms()), ' atoms')
                chain = Chain(chain_id = x, chain_type = 'ligand', chain_name = chain_name, chain_view = listLigand[y], is_selected = True, resindices='', is_group = True)
            listChains.append(chain)
        return listChains

    pass


class Variable():
    parsepdb = ParsePdb()

    pass
  