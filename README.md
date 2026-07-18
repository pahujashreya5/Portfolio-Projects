# Project Description: Openusd Reactive Simulation-On-Demand Ingestion

## Overview: Generates dust simulations without an artist ever touching the mouse.
Things to understand before looking at the code: python, python for Houdini, openUSD basics, basic nets in Houdini, Solaris basics, os, some idea about hython

## Planned Data/Instruction Flow:

1. USD Stage sits in memory.
2. Python scanner reads Stage metadata. Walks through pipeline and computes AABBs (Axis-Aligned Bounding Boxes).
3. When intersection is verified, the Python controller marshals the 3D data into strings.
4. Isolated subprocess (using hython) is created.
5. Houdini reads the data and evaluates the DOP network for it. Then writes localized USD data back to disk.
6. Composition Arc is written using main controller to add the simulated geometry back into the scene.

# Master Scene script demo output

[Demo Video](https://github.com/user-attachments/assets/354e573c-fe75-44ec-b510-b29ba3c954da)

# Notes

1. using vex within to run with hython: i had to use vex to manually simulate the dust because popnet wouldn't load into my memory ue to system issues. using vex doesn't load and heavy dopnet with all its nodes and node types, and therefore the it executes super fast. of course, this is in fact taking a step backwards because solaris already has the option to create a popnet in just a few lines but i was not able to do this on my machine so i am leaving this note here for others.
Also, this was very intersting for learning more about how houdini manages things. so popnet is not a c++ hardcoded node in houdini's codebase- it is an HDA (network of nodes in a package), which means it takes a while to load all of the assets when this is called. if, in any case, the load fails, then even accessing any one asset is not possible. in fact even when opening the Houdini application, it takes time to load because it is loading all of these HDAs.
and since hython is instructed to boot as fast as possible, it might sometimes skip loading the HDAs at all, and we end up getting some error like 'a node type is not recognized'.
another fix (other than manually vex scripting) is find and load the required library before we create the popnet. this makes sure hython already has access to the nodes before it ever executes. i will leave both these methods in the code and you can choose which one based on your usecase.
something like a simple dust sim can be written with vex, but there is no point going by this method if your net is going to be complex. that would defeat the purpose of using hython (headless Houdini) at all.
2. using houdini apprentice so dust sim is exporting as .usdnc. not recognized so need to write a plugin using Sdf

# References:

1. [https://openusd.org/dev/tut_xforms.html](https://openusd.org/dev/tut_xforms.html)
2. [https://github.com/kiryha/Houdini/wiki/pixar-usd-python-api](https://github.com/kiryha/Houdini/wiki/pixar-usd-python-api)
3. [https://tokeru.com/cgwiki/HoudiniPython.html](https://tokeru.com/cgwiki/HoudiniPython.html)


### PENDING TASKS
- naming conventions to be corrected
- all demo vids to be added
- diagram workflow to be added
- add tests
- dynamic coordinates in rand for sphere and ground




