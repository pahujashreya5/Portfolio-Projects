# Project Description: Openusd Reactive Simulation-On-Demand Ingestion

# Overview: Generates dust simulations without an artist ever touching the mouse.
Things to understand before looking at the code: python, python for Houdini, openUSD basics, basic nets in Houdini, Solaris basics, os, some idea about hython.

This project is a procedural pipeline built with USD and Python that automatically detects geometry collisions and triggers a simulation in response. It creates a base USD scene containing an animated sphere and a ground plane, scans the timeline for intersection points, and kicks off a headless Houdini process (hython) to simulate a dust impact exactly where and when the collision happens. Finally, the pipeline pulls the exported dust simulation back into the master USD stage so everything plays back seamlessly.

# Data & Instruction flowchart

<img width="3281" height="1575" alt="usd_project_flowchart" src="https://github.com/user-attachments/assets/262ee533-37f8-4e9f-8071-0c17d388b63a" />

The pipeline relies on three main scripts passing data sequentially to generate the final scene:
1. Scene Initialization: A master USD scene is generated with basic geometry and random animation.
2. Intersection Engine: The scene is scanned to find the exact frame and 3D coordinates where the geometry overlaps.
3. Simulation Worker: The hit data is passed as strings through the OS to a headless Houdini instance, which builds, simulates, and exports the particle effect back to disk.

# Demo Output_v1

https://github.com/user-attachments/assets/c2b7c652-cc27-4ae4-a080-6ce323c71931

# Details of code

1. init_script.py (Scene Setup): This script is responsible for setting up the initial USD stage.
  a. Stage Creation: Initializes a new USD stage in memory (stage1.usda) and sets up basic metadata, like setting the up-axis to Z and establishing the time codes from frame 1 to 192.
  b. Geometry Generation: Defines a static ground plane and a sphere using UsdGeom.
  c. Animation: Randomizes the sphere's position across the timeline. It uses UsdGeom.Xformable and Usd.TimeCode to author translation opinions at specific frames, letting USD handle the linear interpolation between points.

3. intersection_engine.py (Collision & Stage Management): This is the brain of the pipeline that connects the USD stage to Houdini.
  a. Bounding Box Calculation: Opens the master scene and computes Axis-Aligned Bounding Boxes (AABB) using UsdGeom.BBoxCache.
  b. Hit Detection: Iterates through the timeline checking for intersections using Gf.Range3d.GetIntersection. When the sphere and ground overlap, it grabs the midpoint of the intersection volume to use as the exact contact point.
  c. Subprocess Execution: Serializes the hit frame and coordinates into strings and fires up hython (Houdini's headless Python interpreter) via the subprocess module. It actively cleans up OS environment variables (like PYTHONPATH and LD_LIBRARY_PATH) before running the command to prevent crashes on systems like macOS.
  d. Payload Integration: Once Houdini finishes rendering, the script loads the resulting .usdnc simulation back into the main stage as a Sdf.Payload. It applies a time shift so the explosion triggers perfectly at the hit frame, and extends the master timeline if the simulation needs more time to play out.

3. houdini_worker.py (Simulation & Baking): This script runs entirely inside Houdini's headless environment.
  a. Data Parsing: Uses argparse to understand the command-line strings (hit frame and XYZ coordinates) passed by the intersection engine.
  b. Network Generation: Procedurally builds a node network in the /obj context. It creates a sphere emitter and scatters 500 points onto it.
  c. VEX Physics: Uses an Attribute Wrangle node with a VEX snippet to drive particle kinematics. The math handles randomized outward directions, per-particle speed, drag (air resistance), gravity, and floor collision. Particles are also scaled down over time using @pscale so they fade out naturally.
  d. Solaris Export: Switches to the /stage context to wrap the generated geometry in a LOP network.
  e. It configures the USD layer metadata and uses a USD ROP node to flatten the stage and export it to disk as dust_sim.usdnc

# Notes

1. using vex within to run with hython: i had to use vex to manually simulate the dust because popnet wouldn't load into my memory ue to system issues. using vex doesn't load and heavy dopnet with all its nodes and node types, and therefore the it executes super fast. of course, this is in fact taking a step backwards because solaris already has the option to create a popnet in just a few lines but i was not able to do this on my machine so i am leaving this note here for others.
Also, this was very intersting for learning more about how houdini manages things. so popnet is not a c++ hardcoded node in houdini's codebase- it is an HDA (network of nodes in a package), which means it takes a while to load all of the assets when this is called. if, in any case, the load fails, then even accessing any one asset is not possible. in fact even when opening the Houdini application, it takes time to load because it is loading all of these HDAs.
and since hython is instructed to boot as fast as possible, it might sometimes skip loading the HDAs at all, and we end up getting some error like 'a node type is not recognized'.
another fix (other than manually vex scripting) is find and load the required library before we create the popnet. this makes sure hython already has access to the nodes before it ever executes. i will leave both these methods in the code and you can choose which one based on your usecase.
something like a simple dust sim can be written with vex, but there is no point going by this method if your net is going to be complex. that would defeat the purpose of using hython (headless Houdini) at all. 
2. using houdini apprentice so dust sim is exporting as .usdnc. not recognized so need to write a plugin using Sdf. Houdini Apprentice Limitations: Because the pipeline runs on the non-commercial Houdini Apprentice version, the simulation is exported as a .usdnc file. As noted in the image_b1828b.jpg flowchart, Solaris natively treats this as a third-party format. To view the final composited result in the Solaris UI, a custom usdnc plugin must be compiled using the usdncFileFormat.cpp and CMakeLists.txt setup.
3. Bounding Box Scalability: The collision detection specifically relies on bounding boxes so that the tool can be scaled up later to handle multiple ground planes and more complex moving primitives.  

# References:

1. [https://openusd.org/dev/tut_xforms.html](https://openusd.org/dev/tut_xforms.html)
2. [https://github.com/kiryha/Houdini/wiki/pixar-usd-python-api](https://github.com/kiryha/Houdini/wiki/pixar-usd-python-api)
3. [https://tokeru.com/cgwiki/HoudiniPython.html](https://tokeru.com/cgwiki/HoudiniPython.html)


### PENDING TASKS
- naming conventions to be corrected
- detailed diagram workflow to be added
- dynamic coordinates in rand for sphere and ground
- add all refs




