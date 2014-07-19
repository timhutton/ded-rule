# Solver for Futoshiki puzzles using deductions only, no search

from itertools import *

row_indices = [ range(i,i+5) for i in range(0,25,5) ]
column_indices = [ range(i,25,5) for i in range(5) ]
subgroups = row_indices + column_indices
possible_values = range(1,6)

max_pigeonhole_size = 3 # (3 is highest because we don't care about subsets of length 4 since remaining location would already be a definite)
value_sets = [ list( e ) for n in range( 1, max_pigeonhole_size+1 ) for e in combinations( possible_values, n ) ]

def get_printable( e ):
    return ''.join(map(str,e)) + ' '*(5-len(e))
        
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
            # for this set of N values, are there N sites with all of them and 5-N sites without any of them?
            N = sum( 1 for e in elements if all( i in e for i in value_set ) )
            num_without_any_of_them = sum( 1 for e in elements if not any( i in e for i in value_set ) )
            if len( value_set ) == N and num_without_any_of_them == 5-N:
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
                    
def inequalities( board, subgroups, greater_thans ):
    for a,b in greater_thans:
        max_a = max( val for val in board[a] )
        min_b = min( val for val in board[b] )
        for i in board[a]:
            if i <= min_b:
                board[a].remove(i)
                return ( 'inequalities', "removed "+str(i)+" from "+str(a)+" because not greater than min of "+str(b) )
        for i in board[b]:
            if i >= max_a:
                board[b].remove(i)
                return ( 'inequalities', "removed "+str(i)+" from "+str(b)+" because not less than min of "+str(a) )

board = [ range(1,6) for i in range(25) ]
greater_thans = [ (1,0),(2,1),(3,4),(5,0),(4,9),(10,5),(9,14),(12,13),(13,14),(17,12),(16,15),(21,16),(21,22),(22,23) ] # Guardian Medium 2014-07-12 (can solve)
greater_thans = [ (0,1),(0,5),(3,8),(5,10),(12,7),(9,14),(13,12),(13,14),(12,17),(17,16),(18,17),(21,16),(18,23),(24,19),(23,24) ] # Guardian Medium 2014-05-10 (can solve)

board[1] = [5]
board[10] = [3]
board[15] = [1]
greater_thans = [ (3,4),(3,8),(9,4),(8,7),(9,8),(10,11),(12,7),(16,17),(17,18),(19,18),(16,21) ] # Guardian Easy 2014-06-28 (can solve)

print_board( board )

rules1 = [ not_allowed_twice, pigeonholes_full ]
rules2 = [ inequalities ]
print
while True:
    r = None
    for rule in rules1:
        r = rule( board, subgroups )
        if not r == None:
            break
    if r == None:
        for rule in rules2:
            r = rule( board, subgroups, greater_thans )
            if not r == None:
                break
    if r == None:
        break   
    type, message = r
    if not type in [ 'not_allowed_twice' ]:
        print message
        print_board( board )
        raw_input( "Press Enter to continue..." )
print
print_board( board )
if sum( len(e) for e in board ) > 25:
    print 'Stuck!'
else:
    # check the answer
    for g in subgroups:
        if not sum( board[e][0] for e in g ) == 15:
            print 'Oops:',g
    for a,b in greater_thans:
        if not board[a]>board[b]:
            print 'Oops:',a,b
    
   