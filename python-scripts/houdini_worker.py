# here we take the strings from our engine and pass them to hython so that it can give houdini the hit frame and coordinates
# argparse is the library used to parse strings (ie, understand string as data/commands)

import sys, argparse, os
from pxr import Usd

try:
    import hou # the houdini library. hython has access to this because it is houdini's compiler. this will only work if this script is run using the hython compiler. python will throw error because it does not know this library.
    # although the hom docs give a way of running this using standard python interpreter: https://www.sidefx.com/docs/houdini/hom/cb/hipfile.html
    print("imported hou")
except ImportError:
    print("make sure to  you are using HYTHON and NOT standard PYTHON interpreter.")
    sys.exit(1) # we tell the subprocess to shut down immediately

def DustSimulationBuildAndExport(frame, x, y, z):
    # check this before doing anything else
    # CheckHDALoaded()
    print("starting building sim")
    # now we use python script to create the dust sim https://www.sidefx.com/docs/houdini/hom/hou/index.html

    # we need to set the timeline so that sim is spawned at hit frame and we decide its life
    start_frame=frame # which we got from our dispatch file output
    life=45 # we can tweak this according to how the dust looks finally
    end_frame=frame+life
    hou.playbar.setFrameRange(start_frame, end_frame) # we just set the start and end for the timeline that you see at the bottom of houdini's GUI. see animation section of the HOU docs

    # we create a houdini object so that it does the simulation work for us
    obj_context=hou.node('/obj')
    # we tell the houdini object to create a new node in which we will create a node network for a dust simulation. the type is geometry and the name is dust
    dust_node=obj_context.createNode('geo', 'dust')
    # let's create the node which will emit dust
    # this means: we enter the dust geo root node and create a node called emitter. it is just a sphere
    emitter=dust_node.createNode('sphere', 'emitter_geom')
    # this is the source of our dust particles and we need it to be at the hit contact point
    emitter.parm('tx').set(x)
    emitter.parm('ty').set(y)
    emitter.parm('tz').set(z)
    size=0.2 # we want tiny dust particles
    emitter.parm('scale').set(size)

    print("starting popnet building")

    # refer to note 1 in readme in case of node not recognized error
    # now we create the particle network (popnet)
    popnet=dust_node.createNode('dopnet', 'dust_simulation') # we add a popnet node to the network and call it dust_simulation
    # popnet=dopnet.createNode('popnet')  
    # now we need to use the particles that we created before as input
    print("popnet node added")
    popnet.setInput(0, emitter) # tells houdini object to connect the emitter to the first(0) input of our popnet node

    popsource=popnet.createNode('popsource', 'src_particles') # access the source node natively living inside houdini
    # print("popsource node created", popsource)
    # now we set some channel values and attributes to make the particles behave like dust being emitted
    popsource.parm('constantactivate').set(0) # we dont want infinite stream of particles so set it to off
    # print("set const activation off")
    
    # print("set count of popsource impulse")
    # just add an hscript expression into the channel where we define conditions for the sim. we need it to begin when frame is start_frame
    popsource.parm('impulseactiveate').setExpression(f"$F=={start_frame}")
    count=1000 # let's create 1000 particles as dust for now
    popsource.parm('impulserate').set(count) 
    # print("set start frame for impulse activation")
    # now we dont want them to just be created and sit there so we add an intial velocity (it should look like impact dust when there is a collision)
    print("popnet setup done")
    vel=3.0
    # variance is the name of the attribute that houdini uses for this. let's set all x y and z direction velocities to 3.0 for now
    popsource.parm('velx').set(vel)
    popsource.parm('vely').set(vel)
    popsource.parm('velz').set(vel)

    # let's print something to help with debugging later
    print("dust sim created successfully by houdini. proceeding to export via usd")

    # now let's work on exporting this. we need to use solaris so that it takes the dust simulation that houdini just built, converts it into lightweight USD format and then sends it to our os so that we can do the remaining steps with python script. (basically, we are aiming to store the lightweight sim until we actually have to render it in whichever application you want to. i will use a usd payload, but more on that later)

    # we need to change from object/geometry context to solaris context
    stage_context=hou.node('/stage') # switch from build to solaris
    # import the sim into our usd stage using a sop

    camera = stage_context.createNode('camera', 'render_cam')

    camera.parm('tx').set(x)
    camera.parm('ty').set(y + 2.0)
    camera.parm('tz').set(z + 5.0)

    camera.parm('rx').set(-22)
    camera.parm('ry').set(0)
    camera.parm('rz').set(0)

    camera.parm('focalLength').set(35)

    print("creating sop import")
    sop_import=stage_context.createNode('sopimport', 'sop_import_node')
    print("created sop import")
    sop_import.parm('soppath').set(popnet.path())
    print("set soppath to popnet.path()", popnet.path())
    usd_rop_node=stage_context.createNode('usd_rop', 'usd_rop_node')

    print("created usd rop node")
    usd_rop_node.setInput(0, sop_import)
    print("set usd rop import")

    # name of output file
    out_filename="$HIP/dust_sim.usdnc"
    print("created output filename")
    # set the name. the node is called lopoutput in houdini
    # actuall .usdnc is the extension for non commercial (apprentice) houdini, which i use. it is identical to .usda, just that it won't work with other DCCs. (will be encrypted for them)
    usd_rop_node.parm('lopoutput').set(out_filename)
    print("set output file name")
    # usd_rop_node.parm('defaultsavestyle').set('usda')
    usd_rop_node.parm('trange').set(1) # we tell usd that below we will specify frame range to render
    # set start and end frames for render
    usd_rop_node.parm('f1').set(start_frame) 
    usd_rop_node.parm('f2').set(end_frame)
    print("set frames")

    # required because otherwise hython doesn;t understand ouput loaction and we would have to specify a layer. but we dont need layers for this simple scene
    usd_rop_node.parm('savestyle').set('flattenstage')
    # usd_rop_node.parm('erroronsavenodepath').set(0)

    print("starting simulation baking")
    usd_rop_node.parm('execute').pressButton() # finally, render!
    # print(out_filename.path())
    print("bake complete 🤯")

# to execute the above script
def main():
    parser=argparse.ArgumentParser(description="houdini worker")
    parser.add_argument('--frame', type=int, required=True, help="hit_frame_number")
    parser.add_argument('--x', type=float, required=True, help="x coord of contact point")
    parser.add_argument('--y', type=float, required=True, help="y coord of contact point")
    parser.add_argument('--z', type=float, required=True, help="z coord of contact point")

    args=parser.parse_args() # store the data in the args variable

    print(f"houdini worker received data {args.frame}, ({args.x}, {args.y}, {args.z})")

    DustSimulationBuildAndExport(args.frame, args.x, args.y, args.z) 

    print("sim exported. houdini worker shutting down")

    sys.exit(0) # make sure to shut down the worker so that it doesn't use memory after it has finished its job

if __name__=="__main__":
    main()



