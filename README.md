#ViLAS tool
##Need software

1. Python version >= 2.7
`sudo apt-get install python python-setuptools python-dev python-augeas python-opengl python-imaging python-pyrex python-pyside.qtopengl python-qt4 python-qt4-gl python-lxml`

2. Gromacs version >= 4.6
`sudo apt-get install gromacs`

3. Cython:
`sudo apt-get install cython`
or
`sudo pip install cython`

4. Openbabel
`sudo apt-get install openbabel`
or 
`sudo pip install openbabel`

5. Scipy
`sudo pip install scipy`

6. Avogadro for python
`sudo apt-get install avogadro`

7. Pymol
`sudo apt-get install pymol`

8. Xmgrace
`sudo apt-get install grace`

9. ANTECHAMBER - download: http://ambermd.org/AmberTools14-get.html
```
tar xvfj AmberTools14.tar.bz2
cd amber14
export AMBERHOME=/<directory>/amber14
./configure gnu
make install
nano ~/.bashrc
-> export AMBERHOME=/<directory>/amber14
-> export PATH=$AMBERHOME/bin:$PATH
source ~/.bashrc
```


##How to install ViLAS in Ubuntu
1. Install pip
`sudo apt-get install python-pip`
2. Install ViLAS
`sudo pip install ViLAS`

##If you get error while installing, maybe it lacks some below packages

** Missing openGL:
```
sudo apt-get install build-essential
sudo apt-get install freeglut3-dev
```

** Missing pygame:
`sudo apt-get install python-pygame`
or
`sudo pip install hg+http://bitbucket.org/pygame/pygame`

** Missing some package
```
sudo apt-get installgcc swig dialog

sudo apt-get install -y python-pip build-essential libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

sudo apt-get install libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0

sudo apt-get install xmlsec1 openssl libxmlsec1 libxmlsec1-dev

sudo apt-get install build-essential autoconf libtool pkg-config  idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus libgle3
```
