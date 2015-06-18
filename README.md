# ScansionPublic
INTRODUCTION
------------
This project is intended to automate the scansion of Latin prose. Currently, only the actual scansion file
(autoscan.py) is complete. A Latin macronizer, which will mark long vowels automatically, and a proper
clean text program (see opening docstring of autoscan.py) are currently in production.

Please direct any questions/concerns to joseph.kirby12@ncf.edu

AUTHORS
-------
Tyler Kirby

Bradley Baker

REQUIRMENTS
-----------
Python 3.4.2 | Anaconda 2.1.0

RUN-TIME INSTRUCTIONS
---------------------

Run autoscan.py in Python 3.4.2 and enter the file path of the Latin text you wish to analyze. The scansion of the file will be returned as a list, with each element in the list representing the scansion of the corresponding sentence.

Example:
~/test.txt = 'quō usque tandem abūtēre, Catilīna, patientiā nostrā aetatis. quam diū etiam furor iste tuus nōs ēlūdet.'

Input: ~/test.txt
Output: ['-u-u--uuu-uuu-u----u', '-u-u-uu-uu----u']

VERSION
-------

Current Version: 0.1

Version 0.1:
+ Added scansion program

LICENSE
-------
MIT License

