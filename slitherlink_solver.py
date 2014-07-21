# Solver for Slitherlink puzzles using deduction rules only, no search
# rules from: https://code.google.com/p/slinker/

from itertools import *

def print_board( b, X, Y, xchar ):
    for y,row in enumerate( b[ i : (i+2*X+3) ] for i in xrange(0,(2*X+3)*(2*Y+3),2*X+3) ):
        if y<1 or y>=2*Y+2: continue
        for x,i in enumerate( row ):
            if x<1 or x>=2*X+2: continue
            if x%2==y%2==1: print '+', # corners
            elif x%2==y%2==0: # cells
                if i >= 0: print str(i),
                else: print ' ',
            elif i==0: print xchar,
            elif i==1:
                if y%2==1: print '-',
                else: print '|',
            else: print ' ', # unknown border
        print
        
def pos( x, y, X, Y ):
    return x + y*(2*Y+3)
def cellpos( x, y, X, Y ):
    return pos( 2*x+2, 2*y+2, X, Y )
def from_string( X, Y, s ):
    board = [ -1 for i in range( (2*X+3)*(2*Y+3) ) ]
    for x in range(1,2*X+3,2):
        board[ pos(x,0,X,Y) ] = 0
        board[ pos(x,2*Y+2,X,Y) ] = 0
    for y in range(1,2*Y+3,2):
        board[ pos(0,y,X,Y) ] = 0
        board[ pos(2*X+2,y,X,Y) ] = 0
    for i,c in [ (i,c) for (i,c) in enumerate(s) if not c=='.' ]:
        board[ cellpos( i%X, i//X, X, Y ) ] = int( c )
    return X,Y,board
    
def stored_rule( board, X, Y, rules ):
    for required,implied in rules:
        for ti in xrange(8):
            req = [ transform(x,y,v,ti) for x,y,v in required ]
            imp = [ transform(x,y,v,ti) for x,y,v in implied ]
            for cell_x,cell_y in list( product( range(-1,X+2), range(-1,Y+2) ) ):
                x,y = 2*cell_x, 2*cell_y
                if not all( 0<=(x+dx)<(2*X+3) and 0<=(y+dy)<(2*Y+3) for dx,dy,val in req ): continue
                if not all( board[ pos(x+dx,y+dy,X,Y) ]==val for dx,dy,val in req ): continue
                if not all( 0<=(x+dx)<(2*X+3) and 0<=(y+dy)<(2*Y+3) for dx,dy,val in imp ): continue
                if all( board[ pos(x+dx,y+dy,X,Y) ]==val for dx,dy,val in imp ): continue
                for dx,dy,val in imp:
                    board[ pos( x+dx, y+dy, X, Y ) ] = val;
                return ( 'stored_rule', 'applied changes' )
                            
def transform( x, y, val, i ):
    # apply one of the 8 rigid-body transforms around this point (rotations and reflections)
    t = [ (x,y),(-y,x),(-x,-y),(y,-x),(x,-y),(y,x),(-x,y),(-y,-x) ]
    tx,ty = t[i]
    return tx,ty,val
    
rule_lines = open( 'slitherlink_rules/solving_rules_5.txt').readlines()
rules = groupby( rule_lines, lambda x: x in [ 'required:\n','implied:\n' ] or x[0] in '#\n' )
rules = [ [ tuple( int(val) for val in line[:-1].split(',') ) for line in lines ] for tf,lines in rules if not tf ]
rules = [ ( rules[i], rules[i+1] ) for i in xrange( 0, len(rules), 2 ) ]
# each rule is expressed as two lists of triples: required and implied
# each triple is (x,y,tf) where x and y are offsets from the cell and tf is 1/0 for true/false
# an X*Y slitherlink grid is stored as (2X+1)*(2Y+1) of walls and cells (see print_board)

# https://en.wikipedia.org/wiki/Slitherlink#mediaviewer/File:Slitherlink-example.png ('moderately difficult') (gets stuck)
X,Y,board = from_string( 6, 6, '....0.33..1...12....20...1..11.2....' )

# http://www.nikoli.co.jp/en/puzzles/slitherlink.html (can solve)
X,Y,board = from_string( 8, 8, '.0.1..1..3..23.2..0....0.3..0......3..0.1....3..3.13..3..0..3.3.' )

# http://www.kwontomloop.com/ sample (can solve)
X,Y,board = from_string( 4, 4, '32.3...23...3.31' )

ded_rules = [ stored_rule ]
print_board( board, X, Y, ' ' )
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
    print_board( board, X, Y, 'x' )
    #raw_input( "Press Enter to continue..." )
if any( board[i] < 0 for i in xrange(1,len(board),2) ):
    print 'Stuck!'
else:
    print
    print
    print_board( board, X, Y, ' ' )

