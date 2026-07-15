# here we take the strings from our engine and pass them to hython so that it can give houdini the hit frame and coordinates
# argparse is the library used to parse strings (ie, understand string as data/commands)

import sys, argparse

try:
    import hou # the houdini library. hython has access to this because it is houdini's compiler. this will only work if this script is run using the hython compiler. python will throw error because it does not know this library.
except ImportError:
    print("run with hython and not standard python.")
    sys.exit(1) # we tell the subprocess to shut down immediately

def main():
    parser=argparse.ArgumentParser(description="houdini worker")
    parser.add_argument('--frame', type=int, required=True, help="hit_frame_number")
    parser.add_argument('--x', type=float, required=True, help="x coord of contact point")
    parser.add_argument('--y', type=float, required=True, help="y coord of contact point")
    parser.add_argument('--z', type=float, required=True, help="z coord of contact point")

    args=parser.parse_args() # store the data in the args variable

    print("houdini worker received data {args.frame}, ({args.x}, {args.y}, {args.z})")

    # DUST SIM HERE

    sys.exit(0) # make sure to shut down the worker so that it doesn't use memory after it has finished its job

if __name__=="__main__":
    main()

