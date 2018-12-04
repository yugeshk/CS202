import sys
import os
import numpy as np
import random
import copy
import time
num_steps = 0
sys.setrecursionlimit(100000)
class Node(object):
    """
    Creates a node for the Semantic Tableaux
    Args:
        object: Instance of the parent Node
    Arrtibutes:
        child_number: The child number of self wrt its parent
        number_of_children: The total number of childen self can have
    """

    def __init__(self, arg=None, proposition=None, clause=None):
        self.frequency = {}
        self.clauses = []
        #self.arg = arg
        if arg is not None:
            self.parent=arg
            self.clauses = []
            #self.clauses = copy.copy(arg.clauses)
            self.frequency = copy.deepcopy(arg.frequency)
            self.update_clauses(proposition = proposition, clause = clause)


    def update_clauses(self, proposition=None, clause=None):
        """
        Applies the said proposition to the clause
        Args:
            self: the current node
            proposition: The proposition that is to be applied
            clause: The clause to be dropped
        """
        for k in proposition:
            p = k
            break

        for c in copy.deepcopy(self.parent.clauses):
            if p in c.keys():
                if (c[p]==proposition[p]):
                    for key in c.keys():
                        self.frequency[key]-=1
                else:
                    self.frequency[p]-=1
                    c.pop(p)
                    self.clauses.append(c)
            else:
                self.clauses.append(c)

        self.clauses.append(copy.deepcopy(proposition))
        for k in proposition:
            self.frequency[k]+=1

        self.unit_propagation()

    def unit_propagation(self):
        """
        Performs unit propogation across the clause list
        """
        flag = True
        while(flag):
            flag = False
            i = 0
            while(i < len(self.clauses)):
                c = self.clauses[i]
                if len(c)==1:
                    for p in c:
                        if(self.frequency[p]>1):
                            flag = True
                            j = 0
                            while(j < len(self.clauses)):
                                c1 = self.clauses[j]
                                if(self.frequency[p]==1):
                                    break
                                if j!=i and p in c1.keys():
                                    if c[p] == c1[p]:
                                        for key in c1:
                                            self.frequency[key]-=1
                                        self.clauses.remove(c1)
                                        if(j<i):
                                            i-=1
                                        j-=1
                                    else:
                                        self.frequency[p]-=1
                                        c1.pop(p)
                                        if(len(c1)==0):
                                            flag = False
                                j+=1
                i+=1
def parse_input(input_fp):
    """
    Parses the DIMACS file input to feed to the SAT solver.
    Args:
        input_fp: file pointer to the input file
    Return:
        final_l: list of dicts that has the input clauses
    """
    flag = True
    while(True):
    	detail_line = input_fp.readline().split()
    	if(detail_line[0]!='c'):
    		break
    if(detail_line[1]!='cnf'):
        print('Input not in CNF form. Please rectify')
        exit()
    num_propositions = detail_line[2]
    num_clauses = int(detail_line[3])
    final_l = []
    n = Node()
    for i in range(num_clauses):
        l = input_fp.readline().split()
        l1 = dict()
        flag = True
        for j in range (len(l)-1):
            if abs(int(l[j])) not in l1.keys():
                if abs(int(l[j])) in n.frequency:
                    n.frequency[abs(int(l[j]))]+=1
                else:
                    n.frequency[abs(int(l[j]))]=1
            else:
                if(int(l[j])>0 and l1[abs(int(l[j]))]=="+"):
                    continue
                if(int(l[j])<0 and l1[abs(int(l[j]))]=="-"):
                    continue
                flag = False
                  
            if(int(l[j])>0):
                l1[abs(int(l[j]))]="+"
            else:
                l1[abs(int(l[j]))]="-"
        #li["length"] = len(l)-1
        if flag:
            final_l.append(l1)
        else:
            for key in l1.keys():
                n.frequency[key]-=1
    n.clauses=final_l
    print(final_l)
    return n

def semantic_tableaux(root_node):
    """
    Look for a model for the given formula set
    Args:
        root_node: Inital set of clauses
    """
    solution = beta_reduction(root_node)
    if(solution):
        print("Check output at model.txt")
    else:
        print("UNSAT")

def negate_proposition(p):
    """
    Negates the passed proposition
    Args:
        p: the proposition to flip
    """
    for key in p:
        if p[key]=="+":
            p[key]="-"
        else:
            p[key]="+"

    return p

def beta_reduction(node):
    global num_steps
    """
    Performs beta reduction on the passed node
    Args:
        node: Node object to reduce
    Return:
        Boolean value of whether solution was obtained
    """
    split_key = split_key_hurestics(node)
    if(split_key != None):
        split_clause = split_clause_hurestics(node,split_key)
    if(split_key == None):
        for c in node.clauses:
            if(len(c)>1):
                split_clause = c
                for k in c.keys():
                    split_key = k
                    break
                break

    #split_proposition = {split_key:split_clause[split_key]}
    """for c in node.clauses:
        if len(c) > 1:
            split_clause = c
    for k in split_clause.keys():
        split_key = k """
    split_proposition = {split_key:split_clause[split_key]}
    #print(node.frequency)
    #print(node.clauses)
    #print(split_clause)
    #split_proposition = split_clause_hurestics(node, split_clause)
    new_node_1 = Node(node, proposition = split_proposition, clause= split_clause)
    num_steps+=1
    #print(num_steps)
    #print(split_clause)
    check = check_node(new_node_1)
    #print(check)
    #print(check)
    if (check == 1):
        print_solution(new_node_1)
        return True
    elif (check == 2):
        pass
    else:
        r = beta_reduction(new_node_1)
        if r == True:
            return True

    new_node_2 = Node(node, proposition = negate_proposition(split_proposition), clause = None)
    check = check_node(new_node_2)
    if (check == 1):
        print_solution(new_node_2)
        return True
    elif (check == 2):
        pass
    else:
        r = beta_reduction(new_node_2)
        if r == True:
            return True

    return False

def beta_reduction_old(node):
    """
    Performs beta reduction on the passed node
    Args:
        node: oject of Node
    Return:
        Boolean value of whether a solution was obtained
    """
    node.number_of_children = len(split_clause)
    while(node.child_number<node.number_of_children):
        split_proposition = split_clause_hurestics(node, split_clause)
        new_node = Node(node, proposition = split_proposition, clause = split_clause)
        node.child_number+=1
        split_clause.pop(list(split_proposition)[0])
        if(check_node(new_node) == 1):
            print_solution(new_node)
            return True
        elif (check_node(new_node) == 2):
            break
        else:
            r = beta_reduction(new_node)

    return False

def check_node(node):
    """
    Checks if the node is closed or in a possible solution state
    Args:
        node: The node to be tested
    Return:
        flag:
            1 - A solution was found
            2 - The node has closed
            3 - The node has to be reduced further
    """
    #First start to check if it is in solution state
    #This is done by seeing if all clauses are atmoic

    flag = 1
    for clause in node.clauses:
        if (len(clause.keys()) == 0):
            flag = 2
            break
    if flag!=1:
        return flag
    for clause in node.clauses:
        if (len(clause.keys()) > 1):
            #print(clause)
            flag = 3 #This means there are unopened clauses
            break

    #Closed Node

    return flag

def print_solution(node):
    """
    Writes out a model for the set of formulae to model.txt
    Args:
        node: The node at with the solution was found
    """
    #Dont need to do this now. Can be donew using the frequency in the node
    output_fp = open("model.txt", "w+")
    output_fp.write("SAT\n")
    #for i in range (1,num_propositions):
    #    for p in node.clauses:
    #       if i in p.keys():
    #           output_fp.write("{}{} ".format(p[i], i))
    #       else:
    #           output_fp.write("{} ").format(i)

    flat_clause_dict = {}
    for c in node.clauses:
        flat_clause_dict.update(c)

    for key in node.frequency.keys():
        if node.frequency[key]==1:
            if flat_clause_dict[key]=="+":
                output_fp.write("{} ".format(key))
            else:
                output_fp.write("{}{} ".format(flat_clause_dict[key], key))
        else:
            output_fp.write("{} ".format(key))

    output_fp.write("\n")
    output_fp.close()

def select_clause_hurestics(node):
    """
    Decides which clause to split
    Args:
        node: object of Node
    Return:
        index of the selected clause
    """
    max_score = 0
    clause_index = 0
    for clause in node.clauses:
        score = 0
        for p in clause.keys():
            score+=node.frequency[p]
        if score>max_score:
            max_score = score
            clause_index = clause

    return clause_index

def split_clause_hurestics_old(node, clause):
    """
    Decides which preposition to split at for the given node??
    Args:
        node: object of current Node
    Return:
        the proposition in {p: "+/-"} format
    """
    for key in clause.keys():
        max = key
        break

    for key in clause.keys():
        if(node.frequency[key]>node.frequency[max]):
            max = key

    return {key: clause[key]}

def split_key_hurestics(node):
    """
    Decides which clause to split
    Args:
        node: object of Node
    Return:
        index of the selected clause
    """
    max = 0
    for key in node.frequency.keys():
        if node.frequency[key] > max:
            max = node.frequency[key]
            max_key = key
    if(max > 1):
        return max_key
    else:
        return None

def split_clause_hurestics(node, key):
    """
    Decides which preposition to split at for the given node??
    Args:
        node: object of current Node
    Return:
        the proposition in {p: "+/-"} format
    """
    """min = 10000
    for c in node.clauses:
        if key in c.keys():
            if len(c) < min:
                min = len(c)
                clause = c"""
    for c in node.clauses:
        if key in c.keys() :
            clause = c
            break
    return clause

if __name__ == '__main__':
    input_file_name = sys.argv[1]
    input_fp = open(input_file_name, 'r+')
    initial_node = parse_input(input_fp)
    input_fp.close()
    start = time.time()
    semantic_tableaux(initial_node)
    end = time.time()
    print("time required : {}".format(end - start))
    print("total number of steps (clauses broken down) : {}".format(num_steps))


