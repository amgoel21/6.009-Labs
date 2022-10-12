#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    formula is a nested list.
    Inside lists are made of tuples of a variable followed by boolean

    Returns None or dictionary with boolean assigned to each variable(which are keys)

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    conditions = dict() # Final dictionary to be returned
    if(len(formula)==0):
        return {}
    for i in formula:
        if len(i)==0: # We set this by definition
            return None
    for i in formula:
        if len(i)==1:
            if(i[0][0] in conditions.keys()): # This condition does not follow variable's value
                return None
            conditions[i[0][0]]=i[0][1]
            newform = tryform(formula,i[0][0],i[0][1]) # Sets first variable to condition value
            other=satisfying_assignment(newform) # Solve previous statement problem
            if(isinstance(other,dict)):
                conditions.update(other)
                return conditions
            else:
                return None
    conditions[formula[0][0][0]]=True
    newform=tryform(formula,formula[0][0][0],True)
    d=satisfying_assignment(newform)
    if(isinstance(d,dict)): #If not none
        conditions.update(d)
        return conditions
    conditions[formula[0][0][0]]=False # Previous did not work
    newform=tryform(formula,formula[0][0][0],False)
    d=satisfying_assignment(newform)
    if(isinstance(d,dict)):
        conditions.update(d)
        return conditions
    return None #First variable cannot be True or False. No solution


def tryform(formula,var,value):
    ''' Helper function
    
    We are given a formula, and a variable and its value
    
    Return new formula to take away all conditions that given var value solves and update others
    
    formula is nested list, var is string, value is boolean
    
    Returns nested list, which is subset of formula'''

    newformula=[]
    numands=len(formula)
    arraycheck = []
    for i in range(numands):
        c=0
        for cond in formula[i]:
            if(cond[0]==var):
                if(cond[1]==value):
                    c=1
                    break
                else:
                    c=-1
        arraycheck.append(c) # Checks each or condition to see if satisfied, not changed, or condition needs to be removed
    for i in range(numands):
        c=arraycheck[i]
        if(c==0):
            newformula.append(formula[i]) # Unchanged condition
        elif(c==-1):
            newcond=[]
            for j in formula[i]:
                if(j[0]!=var):
                    newcond.append(j) # Take away other conditions for var
            newformula.append(newcond)
    return newformula # If c==1, condition is solved and ignored


            




def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    constantlst = list(student_preferences.keys())
    numstud=len(constantlst)
    roomlst = list(room_capacities.keys())
    allcond=[]
    for stud in student_preferences.keys():
        cond=[]
        for room in student_preferences[stud]:
            c=(stud+"_"+room,True) # Writes or condition of True for each room in student preference
            cond.append(c)
        allcond.append(cond)
    for stud in student_preferences.keys():
        for i in range(len(roomlst)-1):
            for j in range(i+1,len(roomlst)):
                cond=[]
                c1=(stud+"_"+roomlst[i],False)
                c2=(stud+"_"+roomlst[j],False)
                cond.append(c1)
                cond.append(c2)
                allcond.append(cond) # For each student, makes sure in only one room (False in each room pair)
    def allcombos(names,number,room):
        ''' Creates all combinations of k+1 students not in room for room with capacity k
        names is list, number is # of students in each or statement, room is room name
        Returns list of lists of conditions'''
        conds=[]
        if(len(names)==1):
            conds.append([(names[0]+'_'+room,False)])
            return conds
        if(number==1):
            conds.append([(names[0]+'_'+room,False)])
            d=allcombos(names[1:],1,room)
            for element in d:
                conds.append(element)
            return conds
        if(len(names)==number): # Then all students must be False
            c=[]
            for i in names:
                c.append((i+'_'+room,False))
            conds.append(c)
            return conds
        noconds = allcombos(names[1:],number,room) # Student 0 is in room
        for i in noconds:
            conds.append(i)
        yesconds = allcombos(names[1:],number-1,room) # Student 0 not in room
        for i in yesconds:
            cp = i.copy()
            a=(names[0]+'_'+room,False)
            cp.append(a)
            conds.append(cp)
        return conds
    for room in room_capacities.keys():
        if(numstud<=room_capacities[room]):# Then condition is always followed
            continue
        conditions=allcombos(constantlst,room_capacities[room]+1,room)
        for condition in conditions:
            allcond.append(condition)
    return allcond


        


        


if __name__ == '__main__':
    import doctest
    #_doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags)
    student_preferences = {"student0": ["session1", "session0"], "student1": ["session1", "session2"], "student2": ["session2"]}
    room_capacities = {"session0": 2, "session2": 2, "session1": 1}
    print(boolify_scheduling_problem(student_preferences, room_capacities))
