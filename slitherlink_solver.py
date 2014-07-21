# Solver for Slitherlink puzzles using deduction rules only, no search
# rules from: https://code.google.com/p/slinker/

from itertools import *

def print_board( b, X, Y ):
    for y,row in enumerate( b[i:(i+2*X+1)] for i in xrange(0,(2*X+1)*(2*Y+1),2*X+1) ):
        for x,i in enumerate( row ):
            if x%2==y%2==0: print '+', # corners
            elif x%2==y%2==1: # cells
                if i >= 0: print str(i),
                else: print ' ',
            elif i==0: print 'x',
            elif i==1:
                if y%2==0: print '-',
                else: print '|',
            else: print ' ', # unknown border
        print
        
def pos( x, y, X, Y ):
    return x + y*(2*Y+1)
def cellpos( x, y, X, Y ):
    return pos( 2*x+1, 2*y+1, X, Y )
def from_string( X, Y, s ):
    board = [ -1 for i in range( (2*X+1)*(2*Y+1) ) ]
    for i,c in [ (i,c) for (i,c) in enumerate(s) if not c=='.' ]:
        board[ cellpos( i%X, i//X, X, Y ) ] = int( c )
    return X,Y,board
    
def stored_rule( board, X, Y, rules ):
    for required,implied in rules:
        for r in xrange(4):
            req = [ rotate(xyv,r) for xyv in required ]
            imp = [ rotate(xyv,r) for xyv in implied ]
            for cell_x,cell_y in list( product( range(X), range(Y) ) ):
                x,y = 2*cell_x+1, 2*cell_y+1
                if not all( 0<=(x+dx)<(2*X+1) and 0<=(y+dy)<(2*Y+1) for dx,dy,val in req ): continue
                if not all( board[ pos(x+dx,y+dy,X,Y) ]==val for dx,dy,val in req ): continue
                if not all( 0<=(x+dx)<(2*X+1) and 0<=(y+dy)<(2*Y+1) for dx,dy,val in imp ): continue
                if all( board[ pos(x+dx,y+dy,X,Y) ]==val for dx,dy,val in imp ): continue
                for dx,dy,val in imp:
                    board[ pos( x+dx, y+dy, X, Y ) ] = val;
                return ( 'stored_rule', 'applied changes' )
                            
def rotate( xyv, r ):
    x,y,val = xyv
    rm = [ [1,0,0,1], [0,-1,1,0], [-1,0,0,-1], [0,1,-1,0] ]
    return x*rm[r][0]+y*rm[r][1], x*rm[r][2]+y*rm[r][3], val

rule_lines = open( 'slitherlink_rules/solving_rules_5.txt').readlines()
rules = groupby( rule_lines, lambda x: x in [ 'required:\n','implied:\n' ] or x[0] in '#\n' )
rules = [ [ tuple( int(val) for val in line[:-1].split(',') ) for line in lines ] for tf,lines in rules if not tf ]
rules = [ ( rules[i], rules[i+1] ) for i in xrange( 0, len(rules), 2 ) ]
# each rule is expressed as two lists of triples: required and implied
# each triple is (x,y,tf) where x and y are offsets from the cell and tf is 1/0 for true/false
# an X*Y slitherlink grid is stored as (2X+1)*(2Y+1) of walls and cells (see print_board)

# https://en.wikipedia.org/wiki/Slitherlink#mediaviewer/File:Slitherlink-example.png
X,Y,board = from_string( 6, 6, '....0.33..1...12....20...1..11.2....' )

ded_rules = [ stored_rule ]
print_board( board, X, Y )
while True:
    r = None
    for rule in ded_rules:
        r = rule( board, X, Y, rules )
        if not r == None:
            break
    if r == None:
        break   
    type, message = r
    print
    print
    print_board( board, X, Y )
    raw_input( "Press Enter to continue..." )
if any( board[i] < 0 for i in xrange(1,len(board),2) ):
    print 'Stuck!'

