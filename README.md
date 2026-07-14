# Project Description: Openusd Reactive Simulation-On-Demand Ingestion

## Overview: Generates dust simulations without an artist ever touching the mouse.

## Planned Data/Instruction Flow:

1. USD Stage sits in memory.
2. Python scanner reads Stage metadata. Walks through pipeline and computes AABBs (Axis-Aligned Bounding Boxes).
3. When intersection is verified, the Python controller marshals the 3D data into strings.
4. Isolated subprocess (using hython) is created.
5. Houdini reads the data and evaluates the DOP network for it. Then writes localized USD data back to disk.
6. Composition Arc is written using main controller to add the simulated geometry back into the scene.

# References:

1. [https://openusd.org/dev/tut_xforms.html](https://openusd.org/dev/tut_xforms.html)
2. [https://github.com/kiryha/Houdini/wiki/pixar-usd-python-api](https://github.com/kiryha/Houdini/wiki/pixar-usd-python-api)




