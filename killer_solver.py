# Solves Killer puzzles using only deductions, no search

from itertools import *

row_indices = [ range(i,i+9) for i in range(0,81,9) ]
column_indices = [ range(i,81,9) for i in range(9) ]
tile_offsets = [0,1,2,9,10,11,18,19,20]
tile_start_indices = [0,3,6,27,30,33,54,57,60]
tile_indices = [ [ tile_offsets[i] + tile_start_indices[j] for i in range(9) ] for j in range(9) ]
sudoku_subgroups = row_indices + column_indices + tile_indices
possible_values = range(1,10)

max_pigeonhole_size = 7 # (7 is highest because we don't care about subsets of length 8 since remaining location would already be a definite)
value_sets = [ list( e ) for n in range( 1, max_pigeonhole_size+1 ) for e in combinations( possible_values, n ) ]

def get_printable( e ):
    return ''.join(map(str,e)) + ' '*(9-len(e))
        
def print_board( b ):
    for row in row_indices:
        print ' '.join( get_printable( b[i] ) for i in row )
        
def not_allowed_twice( b, subgroups ):
    for subgroup in subgroups:
        elements = [ b[i] for i in subgroup ]
        for i in possible_values:
            # is this value i definite in any element in this subgroup?
            if any( len(e)==1 and e[0]==i for e in elements ):
                # does value i appear as a possible in any element in this subgroup?
                for e in elements:
                    if len(e)>1 and i in e:
                        e.remove(i)
                        return ( 'not_allowed_twice', "value "+str(i)+" can't appear here because definite elsewhere in this subgroup" )
    
# pigeonholes_full: within a subgroup, if N values can only appear in a common set of N locations, then no 
#                   other values can appear in those locations
#                   (for N=1, this is saying that there is only one location for a value and so it must go there)
def pigeonholes_full( b, subgroups ):
    for subgroup in subgroups:
        elements = [ b[j] for j in subgroup ]
        for value_set in value_sets:
            # for this set of N values, are there N sites with all of them and 9-N sites without any of them?
            N = sum( 1 for e in elements if all( i in e for i in value_set ) )
            num_without_any_of_them = sum( 1 for e in elements if not any( i in e for i in value_set ) )
            if len( value_set ) == N and num_without_any_of_them == 9-N:
                # are there any excess entries in the N sites?
                num_within_N = sum( len(e) for e in elements if any( i in e for i in value_set ) )
                if num_within_N > len(value_set)*N:
                    if len(value_set ) > 2:
                        print_board( b )
                        print subgroup
                        print elements
                        print num_without_any_of_them
                        print num_within_N
                    # remove the excess elements
                    for e in elements:
                        if any( j in e for j in value_set ):
                            for excess_element in set(e).difference(set(value_set)):
                                e.remove( excess_element )
                    return ( 'pigeonholes_full', "pigeonholes are full for set "+str(value_set)+" so removing other elements" )

# intersection: given two subgroups A and B and their intersection: if a value can't appear in A-B
#               then it also can't appear in B-A. (This is because it must appear in the intersection of A and B.)
# (Sudoku Explainer calls this "claiming")
def intersection( b, subgroups ):
    for A in subgroups:
        for B in subgroups:
            if A == B or not any( e in A for e in B ):
                continue # only interested in subgroups that intersect
            a_minus_b = list(set(A).difference(set(B)))
            b_minus_a = list(set(B).difference(set(A)))
            elementsAminusB = [ b[j] for j in a_minus_b ]
            elementsBminusA = [ b[j] for j in b_minus_a ]
            for i in possible_values:
                if not any( i in e for e in elementsAminusB ) and any( i in e for e in elementsBminusA ):
                    print_board( b )
                    print A
                    print B
                    print "A:",[ b[j] for j in A]
                    print "B:",[ b[j] for j in B]
                    print i,"doesn't appear in A-B:",elementsAminusB
                    print "and so shouldn't appear in B-A:",elementsBminusA
                    for e in elementsBminusA:
                        if i in e:
                            e.remove(i)
                    return ( 'intersection', str(i)+" doesn't appear in A-B, so it can't appear in B-A" )
                    
# for the killer groups that add up to a total: only allow those numbers that permit this
def partitions( b, sum_groups ):
    for total,subgroup in sum_groups:
        # can we eliminate any of the numbers in this subgroup because they can't add up to total?
        elems = [ b[i] for i in subgroup ]
        vp = list( p for p in product( *elems ) if sum(p)==total and len(set(p))==len(p) ) # valid permutations
        vd = [ set(e) for e in zip( *vp ) ] # valid digits in each position in the group
        for i in range(len(vd)):
            if not len( elems[i] ) == len( vd[i] ):
                for val in set(elems[i]).difference(vd[i]):
                    elems[i].remove( val )
                return ( 'partitions', "some values can't sum to "+str(total)+" here" )
                
# if two subgroups are nested and the inner one has known digits (modulo permutation) then those values can't appear in the outer one
def nested( b, sudoku_subgroups, sum_groups ):
    for total,A in sum_groups:
        for B in sudoku_subgroups:
            if A==B or not all( e in B for e in A ):
                continue;
            a_elems = [ b[i] for i in A ]
            vp = list( p for p in product( *a_elems ) if sum(p)==total and len(set(p))==len(p) ) # valid permutations
            api = [ i for i in possible_values if all( i in p for p in vp ) ]
            if len( api ) > 0:
                b_minus_a = list(set(B).difference(set(A)))
                elementsBminusA = [ b[j] for j in b_minus_a ]
                for i in api:
                    removed = False
                    for e in elementsBminusA:
                        if i in e:
                            e.remove(i)
                            removed = True
                    if removed:
                        return ( 'nested', "nested subgroup "+str(A)+" must contain "+str(i)+" so can remove from B-A" )
                            
def ind(x,y): return x+y*9  

# make deductions until we can make no more
rules1 = [ not_allowed_twice, pigeonholes_full  ]  # take all subgroups
rules2 = [ intersection ] # take only sudoku_subgroups
rules3 = [ partitions ] # take only sum_groups
rules4 = [ nested ] # take sudoku_subgroups and sum_groups separately
board = [ range(1,10) for i in range(81) ]
sum_groups = [ (17,[0,9,18,19]),(21,[1,2,10,11]),(7,[3,12]),(21,[4,5,14,23]),(17,[6,7,8,15]),
           (8,[13,22]),(30,[16,17,26,35]),(22,[20,21,29,38]),(8,[24,25,34]),(21,[27,28,36,45]),
           (10,[30,31,39,48]),(12,[32,33]),(12,[37,46]),(23,[40,49,50,51]),(21,[41,42,43]),
           (16,[44,53,62,71]),(9,[47,55,56]),(12,[52,61]),(19,[54,63,72]),(24,[57,58,66,75]),
           (18,[59,60,67,68]),(23,[64,65,73,74]),(22,[69,70,78]),(9,[76,77]),(3,[79,80]) ] # Guardian Hard 2014-05-10 (gets stuck)
sum_groups = [ (9,[0,9,10]),(16,[1,2]),(9,[3,12,11]),(19,[4,5,6,13]),(25,[7,8,15,16]),
            (17,[14,23,32]),(9,[17,26]),(22,[18,27,36,45]),(21,[19,20,21,28]),(7,[22,31]),
            (7,[24,25]),(11,[29,30]),(30,[33,34,35,44]),(11,[37,46]),(10,[38,39,40]),
            (22,[41,42,50,51]),(4,[43,52]),(22,[47,56,65,66]),(20,[48,49,57,58]),
            (20,[53,61,62]),(8,[54,63]),(10,[55,64]),(7,[59,60]),(20,[67,74,75,76]),
            (17,[68,69,70,71]),(15,[72,73]),(8,[77,78]),(9,[79,80]) ] # Guardian Hard 2014-07-12 (gets stuck)
sum_groups = [ (14,[0,9]),(6,[1,10]),(15,[2,3,4]),(22,[5,6,15]),(19,[7,8,16,17]),
            (3,[11,12]),(9,[13,22]),(17,[14,23]),(7,[18,19]),(16,[20,21,29]),(13,[24,32,33]),
            (9,[25,26,34]),(30,[27,28,36,37]),(24,[30,31,39,40]),(21,[35,44,52,53]),
            (9,[38,47,56]),(10,[41,50]),(12,[42,43]),(7,[45,54]),(6,[46,55]),(8,[48,49]),
            (8,[51,59,60]),(30,[57,58,66,67]),(15,[61,62]),(20,[63,64,72,73]),(17,[65,74,75]),
            (8,[68,69,70]),(10,[71,80]),(20,[76,77,78,79]) ] # Guardian Hard 2014-06-28 (can solve)
killer_groups = [ b for a,b in sum_groups ]
# validate
if not len( set( e for g in killer_groups for e in g ) ) == 81 or not sum( e for g in killer_groups for e in g ) == sum(range(81)):
    print 'error in table'
    exit()
print_board( board )
print
while True:
    r = None
    for rule in rules1:
        r = rule( board, sudoku_subgroups + killer_groups )
        if not r == None:
            break
    if r == None:
        for rule in rules2:
            r = rule( board, sudoku_subgroups )
            if not r == None:
                break
    if r == None:
        for rule in rules3:
            r = rule( board, sum_groups )
            if not r == None:
                break
    if r == None:
        for rule in rules4:
            r = rule( board, sudoku_subgroups, sum_groups )
            if not r == None:
                break
    if r == None:
        break   
    type, message = r
    if not type in [ 'not_allowed_twice', 'partitions' ]:
        print message
        print_board( board )
        raw_input( "Press Enter to continue..." )
print
print_board( board )
if sum( len(e) for e in board ) > 81:
    print 'Stuck!'
else:
    # check the answer
    for g in sudoku_subgroups:
        if not sum( board[e][0] for e in g ) == 45:
            print 'Oops:',g
    for total,g in sum_groups:
        if not sum( board[e][0] for e in g ) == total:
            print 'Oops:',total,g
    
   