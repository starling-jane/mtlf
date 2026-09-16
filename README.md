# mtlf v0.1
this is a python library providing some basic functions regarding Magic: the Gathering cards, as they're represented by Scryfall as JSON data, along with some basic command line utilities using this library.

`mtlfc` allows for you to search for cards, searching any fields made available by Scryfall using python's regular expressions.

`mtlfp` allows you to generate an A4-printable HTML file of playtest cards based on a card list.

'mtlf' stands for meatloaf, which is my cat's name. 

## notes and disclaimers
this is a personal project for my personal use. you are free to use, modify and redistribute it as you see fit, but no warranty is provided. be aware that nothing here is of any kind of quality whatsoever.

installation in particular is currently highly experimental, rudimentary, doesn't make use of best practices, is designed mostly to work only on my machines, is incomplete, and is highly untested. please do not use the automated installation scripts without reviewing them first.

mtlf.py is located under src and provides the library functions. executables are located under apps and require mtlf.py to be loaded as a module. you should be able to just copy mtlf.py into the apps folder, cd into the apps folder, and run the apps from there. you will probably have to fix the shebang lines of the executables to make them run.

mtlf.py does not query Scryfall at runtime; it opens up a local JSON file of bulk data as kindly provided by Scryfall. it looks for this file in `~/.mtlf/data.json`. see Scryfall's API help docs on how to download this yourself; automated downloading of this file is still to be implemented.

have fun and be yourself

## road map
### v0.2
- automate downloading of scryfall bulk data
- properly detect or query for system python version + fix the shebang lines at install time
- implement an update function in the installer, distinct from the install function
### v0.3
- implement an optional database server daemon (postgres server?) to improve query times
	- (maybe this needs to happen later than the v1.0 stuff)
### v1.0 (?)
- make the python library installable in a clean way with pip or something, instead of 'copy it into /usr/lib/python'
- make the installation process cleaner in general and more portable
- generally make things portable enough that this should be reasonably installable on any unix system
- test everything more on multiple installations until i'm confident in it
### v???
- maybe some sort of PHP webserver frontend stuff?
- possibly at least an HTTP API to interact with it
- directly query Scryfall
	- not doing this unless i can at least parse and respect rate limits
	- mostly i want to be careful to not have this application be a nuclear bomb that explodes scryfall's rate limits and instantly gets you IP banned, which is part of why it currently does not support directly querying Scryfall at all
