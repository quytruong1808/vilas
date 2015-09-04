set dir "/home/superuser/Documents/software_2/caver/input"

mol load pdb ${dir}/protein.pdb

after idle { 
  mol representation NewCartoon 
  mol delrep 0 top
  mol addrep top
  mol modcolor 0 top "ColorID" 8
} 

