# i have used bounding box for collision detection because i intend to progressively add complexity to this project in terms of number of ground planes and more moving primitives other than the sphere

from pxr import Usd, UsdGeom, Gf

def RetrieveScene():
    path='./stage1.usda'
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

def CallSubProcessHython(ground_AABB, sphere_AABB):
    # wake up houdini in background
    print(f"placehloder: calling houdini subprocess")
    return True # on correct execution


if __name__=="__main__":
    stage, ground, sphere=RetrieveScene()
    
    hit_frame, hit_coordinates=FindHit(stage, ground, sphere)

    if hit_frame is not None:
        CallSubProcessHython(hit_frame, hit_coordinates)
    else:
        print(f"no collisions")




    
    
    
