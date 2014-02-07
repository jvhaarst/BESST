INSTALLATION:
--------------

Using pip or easy_install (strongly recommended)
---------------------------------------------------
Python has two package installers, "pip" and "easy_install", which makes it very easy to install BESST. If you have any of this installed,

Type for pip (in terminal):
sudo pip install BESST
Type for easy_install (in terminal): 
sudo easy_install BESST

If you do not have pip or easy_install for python, you can get e.g. pip as follows:

curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python get-pip.py

With proper installation of BESST, you should be able to run:

runBESST

to view user instructions.

(This installation will install the two nonstandard python module dependencies: pysam 0.6, networkx-1.6 automatically for you.)



Installing manually
----------------------

In BESST folder where setup.py is located, run:

python setup.py install

This installation will not include the two modules "networkx" and "pysam". You need to install them separately. They can be found here:

http://networkx.github.com/documentation/latest/install.html

http://code.google.com/p/pysam/downloads/list