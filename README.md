# backupTools
nCurses-based frontend to create/monitor linux configuration files

Consists of 3 major files:
	- backupToolsV2.py		Main program
	- ncengine.py			Curses engine, ncurses library used by main file
	- poktools.py			different tools used by main file



ncEngine:
---------------------
<self>.objects (dict): 		Any object created by the module is placed into this dict and an ID is returned.

<self>.drawStack (list): 	this list contains the IDs of objects to be drawn in loop, in the order in which they are drawn
							Thus, appending and popping id's from this list controls the program
							The last object in this list is always, per definition, the active object



backupTools:
---------------------





Addendum:


List of menu ID's
----------------------------------------------
1 : Unnamed_Label
2 : Unnamed_Label
3 : Unnamed_Label
4 : Unnamed_Label
5 : Unnamed_Label
6 : config file status
7 : apt package status
8 : config file description
9 : apt package description
10 : config file list
11 : apt package list
12 : config files central menu
13 : apt packages central menu
14 : selectionMenuConfig
15 : selectionMenuApt
16 : compareLabelLeft (Original)
17 : compareLabelRight (Backed Up)
18 : compareWindowLeft (Original)
19 : compareWindowRight (Backed Up)
20 : dialogBox
21 : inputBox

