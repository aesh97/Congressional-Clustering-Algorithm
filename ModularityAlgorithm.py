import networkx as nx
import networkx.algorithms.community as nx_comm
import json
from collections.abc import Iterable
import numpy as np
import time



#lines 10 - 30 run before main to set global variables 


#loads json data from specified file
#change file name 
file = open('/Users/adam/Desktop/mydata/117.json', "r")


#data is a list of dictionary objects that store bill data
data = json.loads(file.read())
file.close()


#Removes the house bills so I am only looking at the senate (lines 14 - 27)
unwanted = []
for bill in data:


#when analyzing the house use "== 'Senate'" otherwise use "== 'House'"
    if (bill['originChamber'] == 'House'):
        unwanted.append(bill)



for i in range(len(unwanted)):
    data.remove(unwanted[i])

#creates nodes object and chamber is added after since it is hard to add that atribute at this scope 
def makeObj(obj):
    return {'name': obj["name"], 'state' :obj["state"]}

#this function returns the first n elements of a given array
def newPartHelper(array, n):
    newArray = []
    for i in range(len(array)):
        if (i == n):
            break
        newArray.append(array[i])
    return newArray


def Modularity(G):

    #this list will contain each unique cluster ID after the for loop
    Clusters = []
    for i in range(len(G.nodes())):
        if (not(G.nodes()[i]['cluster'] in Clusters)):
            Clusters.append(G.nodes()[i]['cluster'])


#this dictionary will map cluster ID to a list of node IDs in the cluster
    NodePartition = {}


    for num in Clusters:
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

        
            arrayAppend = []
            
            for i in range(len(index)):
                arrayAppend.append(index[i])
                
                
           
            self.addData(arrayAppend)

            

        #ends recursion    
            return newindex

    
    def permutations(self, numClusters, numNodes):
        # creates a list (numClusters by numClusters by numClusters ... (numNodes times) in numNodes dimesnions where each element is a 0
        shape = []

        for i in range(numNodes):
            shape.append(numClusters)
        shape = tuple(shape)

        array = np.zeros(shape)
        array = list(array)

        

        
            
       
        

        #these lines create every permutation of the clusters the considered nodes could be and appends them to out
        index = []
        out = []
        self.iterate(array,[])
        
            
        

    def getData(self):
        self.permutations(self.numNode, self.numClusters)
        
        return self.data
          
          

def GetNewPartitions(G, n, R, D, I):
    H = G

    #each array stores the nth lowest clustering coef node from each party cluster
    FromR = newPartHelper(R,n)
    FromD = newPartHelper(D,n)
    FromI = newPartHelper(I,n)

    AllNodes = FromR + FromD + FromI
    Baseline = Modularity(G)
    
    maxClust = 0
    BestPartition = G
    for i in range(len(AllNodes)):
        H.nodes()[AllNodes[i]]["cluster"] = 3 + i
        maxClust = 3 + i
        

   
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
    

def makeEdges(G):

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


def makePartyClusters(G, R, D, I):
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

def main():
    
    
    
    

    

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
    makeEdges(G)

    start = time.time()

    

    

#Republican party nodes index
    Rep = []
#democratic nodes
    Dem = []
#independent
    Indep = []


#populates Rep, Dem and Indep with appropriate node indexes
    makePartyClusters(G, Rep, Dem, Indep)


        

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
    ModNow = GetNewPartitions(G,1, Rep, Dem, Indep)

    end = time.time()

    print(((ModNow/atFirst) - 1)*100)
    print(end-start)

    
    
   
    


if __name__=="__main__":
    main()
