# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 17:33:47 2021

@author: Jingxin Zhang
"""

import googlemaps
import requests
import cvxpy as cp
import numpy as np

API_KEY = "AIzaSyCGNDLBDbMc7Y2cvW7ajGV9nFn43hkMXvU"
map_client = googlemaps.Client(API_KEY)

addr = [] # List to store the 15 addresses
addr.append("Ohio Union, Columbus, OH")
addr.append("The Ohio State University RPAC, Columbus, OH")
addr.append("North Recreation Center, Columbus, OH")
addr.append("Thompson Library, Columbus, OH")
addr.append("Science and Engineering Library, Columbus, OH")
addr.append("Ohio State Ice Rink, Columbus, OH")
addr.append("Ohio Stadium, Columbus, OH")
addr.append("Traditions at Scott, Columbus, OH")
addr.append("Traditions at Kennedy, Columbus, OH")
addr.append("Byrd Polar and Climate Research Center, Columbus, OH")
addr.append("Wexner Medical Center, Columbus, OH")
addr.append("Curl Market, Columbus, OH")
addr.append("University Hall, Columbus, OH")
addr.append("Orton Geological Museum, Columbus, OH")
addr.append("The Oval, Columbus, OH")

geocode = [] # List to Store corresponding geocode to an address
for i in range(len(addr)):
    geocode.append(map_client.geocode(addr[i]))
    
# url variable stores distance api url
url ='https://maps.googleapis.com/maps/api/distancematrix/json?'

# Initialize a 15*15 matrix to store the walking distance
Matrix = []
for i in range(15):          # A for loop for row entries
    a = []
    for j in range(15):      # A for loop for column entries
         if i!= j:
             req = requests.request("GET", url + "origins=" + addr[i] + "&destinations="
                                       + addr[j] + "&traffic_mode = walk" + "&key=" + API_KEY)
             response = req.json()
             # get distance in meter from the json dictionary
             distance = response['rows'][0]['elements'][0]['distance']['value']
             Matrix.append(distance)
         else:
             Matrix.append(0)

arr = np.asarray(Matrix)
#Distance Matrix
D = arr.reshape(15,15)
#Walking time Matrix
C = D/1.42
print(D)
print(C)

# xij stands for whether the path from a place numbered i to a place numbered j is taken
x = cp.Variable((15,15), boolean = True)
# ui stands for the time arrived at each place
u = cp.Variable(15, nonneg = True)

global obj_func
obj_func = 0
for i in range(15):
    for j in range(15):
        obj_func += C[i,j]*x[i,j]

constraints = []

# Constraint1 ensures at least 8 places should be visited
global const1
const1 = 0
for i in range(15):
    for j in range(15):
        const1 += x[i,j]
constraints.append(const1 >= 8)

# sumCol(r) is the sum of 1s in column r
def sumCol(r):
    sumC = 0
    for i in range(15):
        sumC += x[i,r]
    return sumC

# sumRow(r) is the sum of 1s in row r
def sumRow(r):
    sumR = 0
    for j in range(15):
        sumR += x[r, j]
    return sumR

# Constraint 2
# Ensures the Ohio Union is the start point
constraints.append(sumRow(0) == 1)
# Constraint 3
# Ensures the Ohio Union is the end point
constraints.append(sumCol(0) == 1)
    
# Constraint 4
# Each column has most one 1, i.e. only one place is visited from each place
for r in range(15):
    constraints.append(sumCol(r)<=1)
    
# Each row has most one 1, i.e. can only visit one place from a place
for r in range(15):
    constraints.append(sumRow(r)<=1)

# Ensures each place is connected
for r in range(2,15):
    constraints.append(x[0,r]+x[1,r]+x[2,r]+x[3,r]+x[4,r]+x[5,r]+x[6,r]+x[7,r]+x[8,r]+x[9,r]+x[10,r]
    +x[11,r]+x[12,r]+x[13,r] == x[r,1]+x[r,2]+x[r,3]+x[r,4]+x[r,5]+x[r,6]
    +x[r,7]+x[r,8]+x[r,9]+x[r,10]+x[r,11]+x[r,12]+x[r,13]+x[r,14])


# Constraint 5
# Ensures that we must visit another place from a place
for i in range(15):
    constraints.append(x[i,i] == 0)


# Constraint 6
# Eliminate subtours
for i in range(2,15):
     constraints.append(u[i] >= 1)
     constraints.append(u[i] <= 14)

for i in range(15):
    for j in range(15):
        if i != j and i!= 0 and j!= 0:
            constraints.append(u[i] - u[j] + 15*x[i,j] <= 14)
            

# Constraint 7
# ensures that Thompson library must be visited
constraints.append(sumCol(3) == 1)

problem = cp.Problem(cp.Minimize(obj_func), constraints)
problem.solve(solver=cp.GUROBI, verbose = True)
print("obj_func = ")
print(obj_func.value)
print("x = ")
print(x.value)