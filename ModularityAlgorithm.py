import networkx as nx
import networkx.algorithms.community as nx_comm
import json
from collections.abc import Iterable
import numpy as np
import time
import tkinter as tk

from tkinter import ttk



#lines 10 - 30 run before main to set global variables 




#creates nodes object and chamber is added after since it is hard to add that atribute at this scope 
def makeObj(obj):
    return {'name': obj["name"], 'state' :obj["state"]}




def Modularity(G):

    #this list will contain each unique cluster ID after the for loop
    Clusters = {}
    for i in range(len(G.nodes())):
        Clusters[G.nodes()[i]['cluster']] = 1


#this dictionary will map cluster ID to a list of node IDs in the cluster
    NodePartition = {}


    for num in Clusters.keys():
        NodePartition[num] = []

    for node in G.nodes():
        NodePartition[G.nodes()[node]['cluster']].append(node)

#this is the iterable we will feed into the modularity function
    NodeList = []


    for key in NodePartition:
        AddArr = []
        for number in NodePartition[key]:
            AddArr.append(number)

        NodeList.append(AddArr)

    return(nx_comm.modularity(G, NodeList, weight = 'weight'))

class getPermData:
    def __init__(self, numNode, numClusters):
        
        self.numNode = numNode
        self.numClusters = numClusters

        self.data = []

    def addData(self, point):

        if not (point in self.data):
            self.data.append(point)

    def iterate(self,obj,  index):

   
        

    

   
    
        newindex = index

        counter = 0

    #if the object is iterable, we iterate over all of its elements and call iterate on it with its location passed to the index argument
        if (isinstance(obj, Iterable)):
            for node in obj:
                newindex.append(counter)

            
                self.iterate(node, newindex)
                newindex.remove(counter)
                counter = counter + 1

        else:

            self.addData(index.copy())

            

        #ends recursion    
            return newindex

    
    def permutations(self, numClusters, numNodes):
        # creates a list (numClusters by numClusters by numClusters ... (numNodes times) in numNodes dimesnions where each element is a 0
        shape = [numClusters] * numNodes

        

        array = np.zeros(shape)

        
        
        

        

        
            
       
        

        #these lines create every permutation of the clusters the considered nodes could be and appends them to out
        
        self.iterate(array,[])
        
            
        

    def getData(self):
        self.permutations(self.numNode, self.numClusters)
        
        return self.data
          
          

def GetNewPartitions(G, n, R, D, I, baseline):
    H = G

    #each array stores the nth lowest clustering coef node from each party cluster

    
    FromR = R[:min(n, len(R))]
    FromD = D[:min(n, len(D))]
    FromI = I[:min(n, len(I))]

    Baseline = baseline

    AllNodes = FromR + FromD + FromI
    
    maxClust = 2+len(AllNodes)
    BestPartition = G
    for i in range(len(AllNodes)):
        H.nodes()[AllNodes[i]]["cluster"] = 3 + i
        
        

   
    #(numClusters,numDimensions) 
    objectiv = getPermData(maxClust,len(AllNodes))

    Permutations = objectiv.getData()

    

   
        
    for posib in Permutations:
        
        
        countter = 0

        
        for i in AllNodes:
            H.nodes()[i]["cluster"] = posib[countter]
            countter = countter + 1
        newMod = Modularity(H)
        

        if (newMod > Baseline):
            
            Baseline = newMod
            BestPartition = H

            H = G


    return(Baseline)

    

   

    

    

    

    



    

    

   
    

def orderByClustCoef(G, nodes):

    #dictionary where node is mapped to its coef
    LocClust = {}

    #desired order of nodes but same elements as nodes stored in newNodes
    newNodes = []

    smallest = 100
    index = 0

    #loops through nodes and calculates clust and stores in LocClust
    for node in nodes:
        
        LocClust[node] = nx.clustering(G, node, weight='weight')
#finds the node with the least clustering coeffecient while data is being generated
        if (LocClust[node] < smallest):
            smallest = LocClust[node]
            index = node

    newNodes.append(index)


#if the output list isn't long enough we search for the node in nodes that has the smallest coef but isn't already in newNodes (append it once found)

    while (len(newNodes) < len(nodes)):
        newSmall = 100
        newindex = 0
        for node in nodes:
            if (node in newNodes):
                continue
            else:
                if (LocClust[node] < newSmall):
                    newSmall = LocClust[node]
                    newindex = node
        newNodes.append(newindex)
    
    return (newNodes)   
                
        
    
#creates the tupple list needed to create nodes (important because of indexing my data for accessing later)  
def makeTupleList(NodeList):
    tupleOut = []

    

    i = 0

    for element in NodeList:
        tupleOut.append((i, element))

        i= i+1
    return tupleOut


#finds the index of a node in the list of G's nodes
def findNode(node, arr):
    for i in  range(len(arr)):
        isEqual = True
#checks for equality by looping through  keys, if there is any difference in the dictionaries they aren't equal to the node we are looking for
        for key in arr[i]:
            if (arr[i][key] != node[key]):
                isEqual = False
        if (isEqual):
            return i
    return -1
    

def makeEdges(G, data):

#loops through bills
    for bill in data:

        #skips if the bill doesn't have a sponsor
        if(bill['sponsor']==[]):
            continue
        else:
    #otherwise the node object is made and we store its location in the graph in SponsGraphIndex
            SponsorNode = makeObj(bill['sponsor'][0])
            SponsorNode['chamber'] = bill['originChamber']

            SponsGraphIndex = findNode(SponsorNode, G.nodes())

            cosponsorsIndex = []
#the locations of all the cosponsor nodes are found and stored in cosponsorsIndex
            for co in bill['cosponors']:
                CoNode = makeObj(co)
                CoNode['chamber'] = bill['originChamber']

                Index = findNode(CoNode, G.nodes())

                if ((Index in cosponsorsIndex) or co['withdrawn'] == True):
                    continue
                else:
                    cosponsorsIndex.append(Index)

#edges are updated or created 
            for coIndex in cosponsorsIndex:
                if (G.has_edge(coIndex, SponsGraphIndex)):
                    G[coIndex][SponsGraphIndex]['weight'] = G[coIndex][SponsGraphIndex]['weight'] + (1/len(cosponsorsIndex))
                else:
                    G.add_edge(coIndex,SponsGraphIndex, weight = (1/len(cosponsorsIndex)))
                    


            
           
            
            
    
    
    print('done making edges')


def makePartyClusters(G, R, D, I, data):
    party = {}

    
    for bill in data:
        if (bill['sponsor'] == []):
            continue
        else:
            SponsNode = makeObj(bill['sponsor'][0])
            SponsNode['chamber'] = bill['originChamber']
            try:

            #if the node has a list associated with it, add the bill party to it
                party[findNode(SponsNode, G.nodes())].append(bill['sponsor'][0]['party'])


               
                        
                        
            except:

                #otherwise associate a list with it
                party[findNode(SponsNode, G.nodes())] = []
#do the same for cosponsors
            for co in bill['cosponors']:
                coNode = makeObj(co)
                coNode['chamber'] = bill['originChamber']
                try:
                    party[findNode(coNode, G.nodes())].append(co['party'])
                except:
                    party[findNode(coNode, G.nodes())] = []
#now that the data is gathered, we analyze (necessary because of party switching)
    for key in party:

        #if a node was both a republican and a democrat during a congress cluster them with the independents
        #if a node was ever independent cluster them with independents
        if ((party[key].count('R') > 0 and party[key].count('D') > 0) or party[key].count('I') > 0):
            I.append(key)
#this means that they were only ever republican
        elif (party[key].count('R') > 0):
            R.append(key)
        else:
#the only other possibility is that they are a democrat
            D.append(key)
        
        
    print("done partitioning by party")



def run(file, n, senate):

    print(file)
       #loads json data from specified file
#change file name 
    file = open('mydata/' + file + '.json', "r")


    


#data is a list of dictionary objects that store bill data
    data = json.loads(file.read())
    file.close()


#Removes the house bills so I am only looking at the senate (lines 14 - 27)
    unwanted = []
    for bill in data:


#when analyzing the house use "== 'Senate'" otherwise use "== 'House'"
        if (bill['originChamber'] == senate):
            unwanted.append(bill)



    for i in range(len(unwanted)):
        data.remove(unwanted[i])
    
    
    
    

    

    nodes = []
    
    G = nx.DiGraph()
    


    #loops through each bill in data
    for bill in data:



      



       #if there isn't a sponors listed the bill is ignored, otherwise a node is created if it is necessary

        try:

           
            SponsObj = makeObj(bill['sponsor'][0])
            SponsObj['chamber'] = bill['originChamber']
            if (not(SponsObj in nodes)):
                nodes.append(SponsObj)
        except:

            continue
        
        
            
       
        

        

    



        
        #nodes are created for cosponsors if necessary

        for co in bill['cosponors']:
          
            CosponsObj = makeObj(co)
            CosponsObj['chamber'] = bill['originChamber']
            if (not(CosponsObj in nodes)):
                nodes.append(CosponsObj)
        
                
    print('done making nodes')

    
   


    #created nodes are added to G

    G.add_nodes_from(makeTupleList(nodes))

    #edges are added to G
    makeEdges(G, data)

    start = time.time()

    

    

#Republican party nodes index
    Rep = []
#democratic nodes
    Dem = []
#independent
    Indep = []


#populates Rep, Dem and Indep with appropriate node indexes
    makePartyClusters(G, Rep, Dem, Indep, data)


        

#orders the 3 cluster by local clustering coeffecient
    
    Rep = orderByClustCoef(G, Rep)

    Dem = orderByClustCoef(G, Dem)

    Indep = orderByClustCoef(G, Indep)
    
    print('done ordering party clusters')

    
    for node in Rep:
        G.nodes()[node]["cluster"] = 2
        
    for node in Dem:
        G.nodes()[node]["cluster"] = 1
    for node in Indep:
        G.nodes()[node]["cluster"] = 0

    atFirst = Modularity(G)

    print('done assigning cluster ID')
   

    

    
    

    

    print('running alg')
    ModNow = GetNewPartitions(G,n, Rep, Dem, Indep, atFirst)

    end = time.time()

    print(((ModNow/atFirst) - 1)*100)
    print(end-start)






 

def main():

    window = tk.Tk()

    window.geometry("200x200")


    


    fileOptions = ["108", "109", "110", "111", "112", "113", "114", "115", "116", "117"]

    

    clicked = tk.StringVar()

    

    clicked.set("108")

    def prt():
        

        run(str(clicked.get()), 1, "House")
        

    drop = tk.OptionMenu(window, clicked, *fileOptions)
    drop.pack()

    label = tk.Label(window, text = " ")
    label.pack()

    button = tk.Button(window, text = "Run Code", command = (prt)).pack()

    window.mainloop()

    

    

 


 

 
    
    
   
    


if __name__=="__main__":
    main()
