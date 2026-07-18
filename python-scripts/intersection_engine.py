# i have used bounding box for collision detection because i intend to progressively add complexity to this project in terms of number of ground planes and more moving primitives other than the sphere

import os, subprocess
from pxr import Usd, UsdGeom, Gf, Sdf

def RetrieveScene():
    path='stage1.usda'
    stage=Usd.Stage.Open(path)
    if not stage:
        raise RuntimeError(f"Failed to open stage at path {path}")
    
    ground=stage.GetPrimAtPath('/Root/ground')
    if not ground:
        raise ValueError(f"Ground prim could not be found")
    
    sphere=stage.GetPrimAtPath('/Root/sphere')
    if not sphere:
        raise ValueError(f"Sphere prim could not be found")
    
    return stage, ground, sphere

def CheckCollisionUsingBoundingBoxes(bbox_cache, ground, sphere, frame):
    # IMPORTANT: we require the world space extent of both the primitives, so that the bounding box adjusts automatically. using the local extent means the bounding box won't adjust when the animation starts.

    # get the time code for current frame
    time_code=Usd.TimeCode(frame)

    # get bbox_cache (used to get world coordinates for bounding box)
    # it will be passed as a parameter when we find the bboxes for each time_code
    bbox_cache.SetTime(time_code)

    # get bounds for both prims
    ground_world_bounds=bbox_cache.ComputeWorldBound(ground)
    sphere_world_bounds=bbox_cache.ComputeWorldBound(sphere)

    # get axis aligned bounding boxes for both prims
    ground_AABB=ground_world_bounds.ComputeAlignedBox()
    if ground_AABB.IsEmpty():
        print(f"ground AABB is empty")
        # return False, None
    sphere_AABB=sphere_world_bounds.ComputeAlignedBox()
    if ground_AABB.IsEmpty():
        print(f"sphere AABB is empty")
        return False, None

    # C++ implementation of finding intersection of 2 bounding boxes in 3D: https://www.pbr-book.org/3ed-2018/Geometry_and_Transformations/Bounding_Boxes
    # openusd has a built in function that we can use simply: GetIntersection
    intersection_vol=Gf.Range3d.GetIntersection(ground_AABB, sphere_AABB)

    if not intersection_vol.IsEmpty():
        contact_point=intersection_vol.GetMidpoint()
        # can return a pair of values: first is whether we have found an intersection or not, and the second value stores coordinate of the midpoint of the volume where both prims intersect. (we say volume because we are working in 3D)
        print("contact point found!")
        return True, contact_point
    print("NO contact point found!")
    return False, None

def FindHit(stage, ground, sphere):
    # we write the loop to find when collision happens using our function

    # TimeCode.Default() is used for initialization to tell that a time code will be written here later
    # the Tokens parameter tells us the PURPOSE of bbox_cache. automatic means it can be used anywhere. the other values could be proxy, render or guide.
    # example here: https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref/usd/transforms/compute-prim-bounding-box.html
    bbox_cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'automatic'])
    print("init bbox cache done")
    # the function GetStartTimeCode can be used to get the beginning time code of our animation timeline from the master scnee that we created
    start_time_code=stage.GetStartTimeCode()
    end_time_code=stage.GetEndTimeCode()
    # convert to frame so that we can pass it to our function
    start_frame=int(start_time_code)
    end_frame=int(end_time_code)

    for frame in range (start_frame,end_frame+1): 
        is_hit, contact_point=CheckCollisionUsingBoundingBoxes(bbox_cache, ground, sphere, frame)
        print(bbox_cache,"\n")
        # i stopped it at one collision for now
        if(is_hit):
            print(f"collision found at {contact_point[0], contact_point[1], contact_point[2]}")
            # we need the contact point to tell houdini where to create sim (origin point)
            return frame, contact_point

    print(f"no collision detected")
    return None, None 

def CallSubProcessHython(hit_frame, contact_point):
    # we need to convert our data to strings so that it can pass through the os and reach hython. this conversion to strings is called SERIALIZATION.
    
    hit_frame_str=str(hit_frame)
    x=f"{contact_point[0]:.3f}" # let's cut it off at 3 decimal places so that the string isn't too long and confusing for when we want to check it
    y=f"{contact_point[1]:.3f}"
    z=f"{contact_point[2]:.3f}"
    #  coord_str = f"{hit_coordinates[0]} {hit_coordinates[1]} {hit_coordinates[2]}"

    # os executes this list of commands
    cmd = [
        "hython", # the subprocess we want to run. (an executable)
        "houdiniWorker.py", # the script with our serialized data that we want to run in the subprocess
        "--frame", hit_frame_str, # the -- is for when this will go into the command line. just the format that needs to be followed in CLI
        "--x", x,
        "--y", y,
        "--z", z,
    ]

    clean_env = os.environ.copy()
    clean_env.pop("PYTHONPATH", None)
    clean_env.pop("DYLD_LIBRARY_PATH", None)
    clean_env.pop("PXR_PLUGINPATH_NAME", None)
    clean_env.pop("DYLD_FRAMEWORK_PATH", None)
    clean_env.pop("LD_LIBRARY_PATH", None)
    # execute subprocess & make suer checks are in place. make sure to put return statements for all the cases to be safe from os freezing etc
    try:
        subprocess.run(cmd, env=clean_env, check=True) # checks in case subprocess crashes. but our python won't crash because of process isolation :)
        print("success")
        return True
    except subprocess.CalledProcessError as e: # in case the subprocess houdini fails/crashes
        print(f"subprocess failed due to error {e}")
        return False
    except FileNotFoundError: # in case we cant find the exec
        # you can replace the word "hython" with path to exec OR set in path to hython zshrc 
        print("could not find hython.")
        return False

    return False # just a fallback

def AddPayloadToStage(master_scene, sim_filepath, frame):
    # adding payload
    stage=Usd.Stage.Open(master_scene, Usd.Stage.LoadAll)
    print("loaded sim")

    sim_path=f"/Root/DustImpact_frame_{frame}"
    sim_prim=stage.DefinePrim(sim_path, "Xform")

    payload_asset = Sdf.Payload(sim_filepath)

    sim_prim.GetPayloads().AddPayload(payload_asset)

    current_end = stage.GetEndTimeCode()
    required_end = float(frame + 24) 

    if required_end > current_end:
        stage.SetEndTimeCode(required_end)
        print(f"Extended master stage timeline end from {current_end} to {required_end} to fit simulation.")
    else:
        print(f"Preserved existing stage timeline (Start: {stage.GetStartTimeCode()}, End: {current_end}).")

    # now save the final scene to disk
    stage.GetRootLayer().Save()
    print("successfully saved final scene with sim")

if __name__=="__main__":
    stage_path='stage1.usda'
    stage_obj, ground, sphere=RetrieveScene() 
    
    hit_frame, hit_coordinates=FindHit(stage_obj, ground, sphere)

    if hit_frame is not None:
        subprocess_success=CallSubProcessHython(hit_frame, hit_coordinates)
        if subprocess_success:
            print("hit_frame is ", hit_frame)
            print("hit_coordinate: ", hit_coordinates)
            sim_cache_path = "/Users/shreyapahuja/USD_Projects/dust_sim.usdnc"
            AddPayloadToStage(stage_path, sim_cache_path, hit_frame)
            print("payload added!")
    else:
        print(f"no collisions")

    # after bake & export complete, we use PAYLOAD in openUSD to load the sim only at render time. we already have the world coordinates in our lightweight sim usd file so we jsut need to create a prim and point to the lcoation of the sim.


    




    
    
    
