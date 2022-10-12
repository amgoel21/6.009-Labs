#!/usr/bin/env python3

import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_internal_representation(nodes_filename, ways_filename):
    """
    Builds dictionary of nodes using nodes and ways file

    Files contain locations(nodes) with latitude/longitude and id

    Ways contains type of path, direction, and the nodes it connects

    Returns dictionary with each node id as key to node. 

    Each node itself is dictionary with latitude, longitude, and set of paths

    Each path contains which node it goes to, distance to node, time to node, and path id

    At beginning, only takes nodes which are in some relevant way
    """
    


    allnodes=set()
    for way in read_osm_data(ways_filename):
        if('highway' in way['tags'].keys()):
            if(way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES):
                for i in way['nodes']:
                    allnodes.add(i) # Set of nodes which are in some relevant path

    atlas={}
    for node in read_osm_data(nodes_filename):
        if(node['id'] in allnodes): # Makes sure in relevant path
            atlas[node['id']] = {'lat':node['lat'],'lon':node['lon'],'paths':set()} # Dictionary entry with id as key
    for way in read_osm_data(ways_filename):
        if('highway' in way['tags'].keys()):
            if(way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES): # Way is of appropriate type
                double=True
                if('oneway' in way['tags'].keys()):
                    if(way['tags']['oneway']=="yes"):
                        double=False # Double-sided road checker
                for i in range(len(way['nodes'])-1):
                    add(atlas[way['nodes'][i]]['paths'],(way['nodes'][i+1],great_circle_distance((atlas[way['nodes'][i]]['lat'],atlas[way['nodes'][i]]['lon']),(atlas[way['nodes'][i+1]]['lat'],atlas[way['nodes'][i+1]]['lon'])),great_circle_distance((atlas[way['nodes'][i]]['lat'],atlas[way['nodes'][i]]['lon']),(atlas[way['nodes'][i+1]]['lat'],atlas[way['nodes'][i+1]]['lon']))/getspeed(way),way['id']))
                    # Path format has node, distance, time, and path id
                    # Time = Distance/Speed
                    if(double):
                        add(atlas[way['nodes'][i+1]]['paths'],(way['nodes'][i],great_circle_distance((atlas[way['nodes'][i]]['lat'],atlas[way['nodes'][i]]['lon']),(atlas[way['nodes'][i+1]]['lat'],atlas[way['nodes'][i+1]]['lon'])),great_circle_distance((atlas[way['nodes'][i]]['lat'],atlas[way['nodes'][i]]['lon']),(atlas[way['nodes'][i+1]]['lat'],atlas[way['nodes'][i+1]]['lon']))/getspeed(way),way['id']))

    return atlas


def getspeed(way):
    '''
    Given way of highway type, return speed as int
    Way is dictionary with tags key

    If tags has maxspeed, return maxspeed value

    Otherwise takes speed from type of highway using Default Speed Library
    '''

    if('maxspeed_mph' in way['tags'].keys()): 
        return way['tags']['maxspeed_mph']
    else:
        return DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]


def add(paths,path):
    '''
    Helper Function utilized in Building Representation
    Adds a path to a node if no other better path to a node

    Take in set of paths and a path
    If set of paths has no other path to same node, add path

    If there is other path to node, checks time between two and keeps better one
    Worse one is removed/not kept in set of paths

    Returns 1 of no value

    '''
    if(len(paths)==0):
        paths.add(path)
    else:
        for i in paths:
            if(i[0]==path[0]):
                if(path[2]<i[2]): # Checks if new path has better time than old path
                    paths.remove(i)
                    paths.add(path)
                return 1
        paths.add(path)                           
    return 1

def addlist(paths,path):
    '''
    Helper Function utilized in Finding best path.
    Similar to above
    
    

    Take in list of long paths and a path
    If set of paths has no other path to same node, add path

    If there is other path to node, checks function between two and keeps smaller one
    Function can be distance/time/heuristic
    Worse one is removed/not kept in set of paths

    Returns 1 of no value

    '''
    if(len(paths)==0):
        paths.append(path)
    else:
        for i in range(len(paths)):
            if(paths[i][0]==path[0]):
                if(path[1]<paths[i][1]): # Checks function of both paths
                    paths[i]=path
                return 1
        paths.append(path)
    return 1


def find_short_path_nodes(map_rep, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    pq=[]
    visited=set()
    atlas=map_rep
    if(node1==node2): # Start spot = End Spot, 
        return [node1]
    for path in atlas[node1]['paths']:
        pq.append([path[0],path[1],[node1,path[0]]]) # All paths from node1 added to queue 
    visited.add(node1)
    a=1
    while(a!=0):
        if(len(pq)==0): # Queue empty so no path from node 1 to node 2
            return None
        k=0
        min=pq[k][1]
        for i in range(len(pq)):
            if(pq[i][1]<min):
                k=i
                min=pq[i][1]
        smallp=pq[k] # Path with smallest distance (or heuristic) in queue
        pq.remove(smallp)
        if(smallp[0]==node2):
            return smallp[2]
        visited.add(smallp[0]) #Found smallest path here, now in visited
        for e in atlas[smallp[0]]['paths']:
            if(e[0] in visited):
                continue
            totaldist=e[1]+smallp[1] # Implement Heuristic here if need-be
            copypath = smallp[2][:]
            copypath.append(e[0])
            addlist(pq,[e[0],totaldist,copypath]) # Add paths from smallest in queue to queue
            
        


    
    

def find_short_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    atlas=map_rep
    loca=0
    locb=0
    dista=-1
    distb=-1
    for node in atlas.keys():
        dist1 = great_circle_distance(loc1,(atlas[node]['lat'],atlas[node]['lon'])) # Find the distance from each node to two coordinates
        dist2 = great_circle_distance(loc2,(atlas[node]['lat'],atlas[node]['lon']))
        if(dista<0):
            loca=node
            locb=node
            dista=dist1
            distb=dist2
        else:
            if(dist1<dista): 
                loca=node
                dista=dist1
            if(dist2<distb): # Check if these nodes are smallest
                locb=node
                distb=dist2
    nodepath = find_short_path_nodes(map_rep, loca, locb) # Find path from node 1 to node 2
    if(nodepath is None):
        return None
    for i in range(len(nodepath)):
        nodepath[i] = (atlas[nodepath[i]]['lat'],atlas[nodepath[i]]['lon']) # Convert to coordinates
    return nodepath
            
            
def find_fast_path_nodes(map_rep, node1, node2):
    """
    Return the fastest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the fastest path (in terms of
        distance) from node1 to node2

    Almost identical to find_short_path_nodes except one noted distance
    """
    pq=[]
    visited=set()
    atlas=map_rep
    if(node1==node2):
        return [node1]
    for path in atlas[node1]['paths']:
        pq.append([path[0],path[2],[node1,path[0]]])
    visited.add(node1)
    a=1
    while(a!=0):
        if(len(pq)==0):
            return None
        k=0
        min=pq[k][1]
        for i in range(len(pq)):
            if(pq[i][1]<min):
                k=i
                min=pq[i][1]
        smallp=pq[k]
        pq.remove(smallp)
        if(smallp[0]==node2):
            return smallp[2]
        visited.add(smallp[0])
        for e in atlas[smallp[0]]['paths']:
            if(e[0] in visited):
                continue
            totaltime=e[2]+smallp[1] # Looks at time instead of distance
            copypath = smallp[2][:]
            copypath.append(e[0])
            addlist(pq,[e[0],totaltime,copypath]) # Takes time as part of path
 
    


def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.

    Almost identical to find_short_path but looks at time    
    """
    atlas=map_rep
    loca=0
    locb=0
    dista=-1
    distb=-1
    for node in atlas.keys():
        dist1 = great_circle_distance(loc1,(atlas[node]['lat'],atlas[node]['lon']))
        dist2 = great_circle_distance(loc2,(atlas[node]['lat'],atlas[node]['lon']))
        if(dista<0):
            loca=node
            locb=node
            dista=dist1
            distb=dist2
        else:
            if(dist1<dista):
                loca=node
                dista=dist1
            if(dist2<distb):
                locb=node
                distb=dist2
    nodepath = find_fast_path_nodes(map_rep, loca, locb) # fast instead of short
    if(nodepath is None):
        return None
    for i in range(len(nodepath)):
        nodepath[i] = (atlas[nodepath[i]]['lat'],atlas[nodepath[i]]['lon'])
    return nodepath


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    atlas = build_internal_representation('resources/midwest.nodes', 'resources/midwest.ways')
    loca=0
    dista=-1
    loc1 = (41.4452463, -89.3161394)
    for node in atlas.keys():
        dist1 = great_circle_distance(loc1,(atlas[node]['lat'],atlas[node]['lon']))
        if(dista<0):
            loca=node
            dista=dist1
        else:
            if(dist1<dista):
                loca=node
                dista=dist1
    print(loca)
    
            

        
    
