from pxr import Usd, UsdGeom, Gf

def CreateStage(file_path):
    # Initializes the stage and sets base metadata
    stage = Usd.Stage.CreateNew(file_path)
    
    # define default root prim
    root_prim = UsdGeom.Xform.Define(stage, '/Root')
    stage.SetDefaultPrim(root_prim.GetPrim())
    
    # Sst stage metadata
    # set up axis +z
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    # setting start and end time codes
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(192)
    stage.SetMetadata('comment', 'Start and end time codes initialized')
    
    return stage

# we give this prim node a path where it lives
def CreateSphere(stage, prim_path):
    # Creates a sphere prim on the provided stage
    sphere = UsdGeom.Sphere.Define(stage, prim_path)
    sphere.GetPrim().SetMetadata('comment', 'created sphere geom')
    
    return sphere

def AnimateSphere(sphere_prim):
    # animating the sphere
    # transformation for sphere
    xform = UsdGeom.Xformable(sphere_prim)
    
    # clearing any previous transformations
    xform.ClearXformOpOrder()
    # adding a transformation operation
    translate_op = xform.AddTranslateOp()
    
    # author opinions at specific timecodes
    # Gf.Vec3d is used to pass precise 3D vector coordinates (x,y,z)
    translate_op.Set(Gf.Vec3d(10.0, 20.0, 30.0), Usd.TimeCode(1))
    translate_op.Set(Gf.Vec3d(10.0, 20.0, 34.0), Usd.TimeCode(192))
    
    sphere_prim.GetPrim().SetMetadata('comment', 'animated sphere')

def main():
    # 1. Initialize the dataset in memory
    file_name = 'stage1.usda'
    stage = CreateStage(file_name)
    
    # 2. Pass the memory object through your modular functions
    sphere = CreateSphere(stage, '/Root/sphere')
    AnimateSphere(sphere)
    
    # commit the final scenegraph to memory
    stage.GetRootLayer().Save()
    print(f"Successfully generated {file_name}")

if __name__ == '__main__':
    main()
