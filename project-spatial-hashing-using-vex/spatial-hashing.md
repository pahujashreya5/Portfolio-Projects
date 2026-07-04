# This is my implementation + breakdown + documentation of spatial hashing using VEX

My work is adapted from the algorithm and C++ code explainde by Ten Minute Physics  
[https://matthias-research.github.io/pages/tenMinutePhysics/11-hashing.pdf](https://matthias-research.github.io/pages/tenMinutePhysics/11-hashing.pdf)  
[https://github.com/matthias-research/pages/blob/master/tenMinutePhysics/11-hashing.html](https://github.com/matthias-research/pages/blob/master/tenMinutePhysics/11-hashing.html)

## The Node Setup

I started by inserting a grid and scattering points on it. The use copy to points so that we have spheres at each of the points. This is because we need a non-zero radius to work with.

<img width="1470" height="956" alt="Screenshot 2026-07-04 at 1 25 01 PM" src="https://github.com/user-attachments/assets/1488616c-058a-48d6-a6f6-7ec1db4d6f0d" />

Make sure we have spacing (which is side length of each cell in the grid) equal to twice the sphere radius. This is the assumption made in our algorithm that enables us to run it for a bounded region of 9 cells (or 27 in 3D).

## Coding The Algorithm + Breakdown Of Code

Here, the algorithm begins. I will first store the points into an array. Then, I will create a dense array which saves memory in case of sparse data like the kind we have. Then, I will move on to the unbounded grid case (we are not limited to 9 cells anymore). Here is where spatial hashing comes into the picture. 

_Step 1:_

