# Solves Sudoku puzzles using only deductions, no search
# see also: Sudoku Explainer

from itertools import combinations

row_indices = [ range(i,i+9) for i in range(0,81,9) ]
column_indices = [ range(i,81,9) for i in range(9) ]
tile_offsets = [0,1,2,9,10,11,18,19,20]
tile_start_indices = [0,3,6,27,30,33,54,57,60]
tile_indices = [ [ tile_offsets[i] + tile_start_indices[j] for i in range(9) ] for j in range(9) ]
subgroups = row_indices + column_indices + tile_indices
possible_values = range(1,10)

max_pigeonhole_size = 7 # (7 is highest because we don't care about subsets of length 8 since remaining location would already be a definite)
value_sets = [ list( e ) for n in range( 1, max_pigeonhole_size+1 ) for e in combinations( possible_values, n ) ]

def printable( e ):
    return ''.join(map(str,e)) + ' '*(9-len(e))
        
def print_board( b ):
    for row in row_indices:
        print ' '.join( printable( b[i] ) for i in row )
        
def not_allowed_twice( b ):
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
def pigeonholes_full( b ):
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
# (Sudoku Explainer calls this "pointing")
def intersection( b ):
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
                    print "A:",[ b[j] for j in A]
                    print "B:",[ b[j] for j in B]
                    print i,"doesn't appear in A-B:",elementsAminusB
                    print "and so shouldn't appear in B-A:",elementsBminusA
                    for e in elementsBminusA:
                        if i in e:
                            e.remove(i)
                    return ( 'intersection', str(i)+" doesn't appear in A-B, so it can't appear in B-A" )
               
# from Sudoku Explainer: if two columns have value i only in two rows then i cannot appear anywhere else in those two rows
# because it must be in one diagonal pair of intersections between rows and columns
# extends to N rows and columns (jellyfish)
def xwing( b ):
    return None
            
def ind(x,y): return x+y*9  

def from_string( s ):
    if not len(s) == 81:
        print( 's not the right length!' )
        exit()
    board = [ range(1,10) for i in range(81) ]
    for i,c in enumerate(s):
        if not c == '.':
            board[i] = [int(c)]
    return board

# make deductions until we can make no more
rules = [ not_allowed_twice, pigeonholes_full, intersection, xwing ]
board = [ range(1,10) for i in range(81) ]
#board = from_string( '.5.....8.6...3...4..92.16....8...2...2..7..5...6...4....59.81..3...2...5.8.....6.' ) # Guardian Hard 2014-07-12
#board = from_string( '.....7.5..8.14...6.5....2..2.....3.....4.8.....9.....2..5....3.4...69.8..9.8.....' ) # Guardian Hard 2014-05-10
#board = from_string( '....2.4...48..6.5.6....8.7..21......4.......5......64..1.3....2.5.9..38...2.5....' ) # Guardian Medium 2014-07-15
#board = from_string( '.3....7..7..4.3.6....6....1.58..6.2...........1.9..48.2....5....9.7.1..8..6....9.' ) # Guardian Hard 2014-06-28
#board = from_string( '..2...8.....4..61....39..2.7....63..42..3..76..31....4.5..74....96..5.....4...2..' ) # http://www.websudoku.com/?level=3&set_id=9676609240 Hard
#board = from_string( '.9...5.1..71.6....6....7.....73....5.68...13.5....84.....4....2....9.87..1.2...4.' ) # http://www.websudoku.com/?level=4&set_id=8969617377 Evil
#board = from_string( '34..............79..5.2..38.6.84.1.....2.7.....3.15.4.92..8.5..75..............64' ) # Web Sudoku Deluxe Extreme Puzzle 16,796,575,067
#board = from_string( '2....81.5..76..8.....2...4.45.9...7...........8...5.64.3...7.....6..92..9.45....3' ) # 48,449,485,611
board = from_string( '3.14.8.6..2......8...1.7...4..38..9...........8..41..5...8.4...7......8..9.5.26.1' ) # 48,426,083,112 (requires intersections)
#board = from_string( '.........96.....58.413.6..9.....5..6..24.97..3..7.....4..5.319.15.....87.........' ) # 58,435,744,106 (can't yet solve this one) (needs xwing)
#board = from_string( '9......8..7.1....6...342...26..8.1....1...7....7.1..43...421...6....9.3..4......5' ) # 60,148,653,814 (can't solve) (needs xwing) 
#board = from_string( '64.....1..5....3.2..3.1......695.7..5.......6..9.725......4.2..8.7....6..9.....38' ) # 66,735,506,770 (can't solve) (needs xwing)
#board = from_string( '8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..' ) # http://www.telegraph.co.uk/science/science-news/9359579/Worlds-hardest-sudoku-can-you-crack-it.html (we can't find any numbers, sudoku explainer needs nested forcing chains...)
print_board( board )
print
while True:
    r = None
    for rule in rules:
        r = rule( board )
        if not r == None:
            break
    if r == None:
        break   
    type, message = r
    #if not type == 'not_allowed_twice':
    #    print message
    #    print_board( board )
    #    raw_input( "Press Enter to continue..." )
print
print_board( board )
if sum( len(e) for e in board ) > 81:
    print 'Stuck!'
else:
    # check the answer
    for g in subgroups:
        if not sum( board[e][0] for e in g ) == 45:
            print 'Oops:',g
