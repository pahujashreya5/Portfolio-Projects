# i have used bounding box for collision detection because i intend to progressively add complexity to this project in terms of number of ground planes and more moving primitives other than the sphere

import os, subprocess
from pxr import Usd, UsdGeom, Gf, Sdf, Kind

def RetrieveScene():
    path='stage1.usda'
    stage=Usd.Stage.Open(path)
    if not stage:
        raise RuntimeError(f'Failed to open stage at path {path}')
    
    ground=stage.GetPrimAtPath('/Root/ground')
    if not ground:
        raise ValueError(f'Ground prim could not be found')
    
    sphere=stage.GetPrimAtPath('/Root/sphere')
    if not sphere:
        raise ValueError(f'Sphere prim could not be found')
    
    return stage, ground, sphere

def CheckCollisionUsingBoundingBoxes(bbox_cache, ground, sphere, frame):
    time_code=Usd.TimeCode(frame)

    bbox_cache.SetTime(time_code)

    # get bounds for both prims
    ground_world_bounds=bbox_cache.ComputeWorldBound(ground)
    sphere_world_bounds=bbox_cache.ComputeWorldBound(sphere)

    # get axis aligned bounding boxes for both prims
    ground_AABB=ground_world_bounds.ComputeAlignedBox()
    if ground_AABB.IsEmpty():
        print(f'ground AABB is empty')
        # return False, None
    sphere_AABB=sphere_world_bounds.ComputeAlignedBox()
    if sphere_AABB.IsEmpty():
        print(f'sphere AABB is empty')
        return False, None

    intersection_vol=Gf.Range3d.GetIntersection(ground_AABB, sphere_AABB)

    if not intersection_vol.IsEmpty():
        contact_point=intersection_vol.GetMidpoint()
        
        print('contact point found!')
        return True, contact_point
    print('NO contact point found!')
    return False, None

def FindHit(stage, ground, sphere):
    bbox_cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'automatic'])
    print('init bbox cache done')
    # the function GetStartTimeCode can be used to get the beginning time code of our animation timeline from the master scnee that we created
    start_time_code=stage.GetStartTimeCode()
    end_time_code=stage.GetEndTimeCode()
    # convert to frame so that we can pass it to our function
    start_frame=int(start_time_code)
    end_frame=int(end_time_code)

    for frame in range (start_frame,end_frame+1): 
        is_hit, contact_point=CheckCollisionUsingBoundingBoxes(bbox_cache, ground, sphere, frame)
        print(bbox_cache,'\n')
        # i stopped it at one collision for now
        if(is_hit):
            print(f'collision found at {contact_point[0], contact_point[1], contact_point[2]}')
            # we need the contact point to tell houdini where to create sim (origin point)
            return frame, contact_point

    print(f'no collision detected')
    return None, None 

def CallSubProcessHython(hit_frame, contact_point):
    # we need to convert our data to strings so that it can pass through the os and reach hython. this conversion to strings is called SERIALIZATION.
    
    hit_frame_str=str(hit_frame)
    x=f'{contact_point[0]:.3f}' # let's cut it off at 3 decimal places so that the string isn't too long and confusing for when we want to check it
    y=f'{contact_point[1]:.3f}'
    z=f'{contact_point[2]:.3f}'
    #  coord_str = f'{hit_coordinates[0]} {hit_coordinates[1]} {hit_coordinates[2]}'

    # os executes this list of commands
    cmd = [
        'hython', # the subprocess we want to run. (an executable)
        'houdiniWorker.py', # the script with our serialized data that we want to run in the subprocess
        '--frame', hit_frame_str, # the -- is for when this will go into the command line. just the format that needs to be followed in CLI
        '--x', x,
        '--y', y,
        '--z', z,
    ]

    clean_env = os.environ.copy()
    clean_env.pop('PYTHONPATH', None)
    clean_env.pop('DYLD_LIBRARY_PATH', None)
    clean_env.pop('PXR_PLUGINPATH_NAME', None)
    clean_env.pop('DYLD_FRAMEWORK_PATH', None)
    clean_env.pop('LD_LIBRARY_PATH', None)
    try:
        subprocess.run(cmd, env=clean_env, check=True) # checks in case subprocess crashes. but our python won't crash because of process isolation :)
        print('success')
        return True
    except subprocess.CalledProcessError as e: # in case the subprocess houdini fails/crashes
        print(f'subprocess failed due to error {e}')
        return False
    except FileNotFoundError: # in case we cant find the exec
        # you can replace the word 'hython' with path to exec OR set in path to hython zshrc 
        print('could not find hython.')
        return False

    return False # just a fallback

def AddPayloadToStage(master_scene, sim_filepath, frame, x, y, z):
    # adding payload
    stage=Usd.Stage.Open(master_scene, Usd.Stage.LoadAll)
    print('loaded sim')

    sim_path=f'/Root/DustImpact_frame_{frame}'
    sim_geom = UsdGeom.Xform.Define(stage, sim_path)
    sim_prim = sim_geom.GetPrim()
    Usd.ModelAPI(sim_prim).SetKind(Kind.Tokens.component)

    sim_prim.GetPayloads().ClearPayloads()
    
    time_shift = Sdf.LayerOffset(offset=float(frame - 1), scale=1.0)
    
    # Target the static localized asset root inside your cache file
    payload_asset = Sdf.Payload(
        assetPath=sim_filepath, 
        # primPath=Sdf.Path('/dust_asset'),
        layerOffset=time_shift
    )
    sim_prim.GetPayloads().AddPayload(payload_asset)

    sim_geom.AddTranslateOp().Set((x, y, z))

    sim_prim.SetInstanceable(True)

    current_end = stage.GetEndTimeCode()
    required_end = float(frame + 45) 

    if required_end > current_end:
        stage.SetEndTimeCode(required_end)
        print(f'Extended master stage timeline end from {current_end} to {required_end} to fit simulation.')
    else:
        print(f'Preserved existing stage timeline (Start: {stage.GetStartTimeCode()}, End: {current_end}).')

    # now save the final scene to disk
    stage.GetRootLayer().Save()
    print('successfully saved final scene with sim')

if __name__=='__main__':
    stage_path='stage1.usda'
    stage_obj, ground, sphere=RetrieveScene() 
    
    hit_frame, hit_coordinates=FindHit(stage_obj, ground, sphere)

    if hit_frame is not None:
        subprocess_success=CallSubProcessHython(hit_frame, hit_coordinates)
        if subprocess_success:
            print('hit_frame is ', hit_frame)
            print('hit_coordinate: ', hit_coordinates)
            sim_cache_path = '/Users/shreyapahuja/USD_Projects/dust_sim.usdnc'
            AddPayloadToStage(stage_path, sim_cache_path, hit_frame, hit_coordinates[0], hit_coordinates[1], hit_coordinates[2])
            print('payload added!')
    else:
        print(f'no collisions')



    




    
    
    
