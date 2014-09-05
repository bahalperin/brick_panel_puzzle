"""brick_panel.py calculates the number of unique panels of a specified
length and height that can be made up of two different types (lengths) of bricks.
The only additional constraint is that the edges of the bricks of adjacent
rows can't line up (See Puzzle pdf for visual).  

Calculation is performed by treating the number of panels that can be made
starting with a unique row as a tree.  The starting row is the root of the tree.
The tree branches off to all the options (adjacent rows) for the starting row.  
All the nodes (rows) in the second tier/level of the tree branch off to their
adjacent rows and so on until the required panel height is reached.  The number
of paths from the root of the tree to an end node of the tree is the number of 
panels that can be made.  brick_panel.py calculates this for each possible row as
a starting row and sums those values to find the total number of panels. 

Data representations:
	Length refers to the length of the brick panel.  Height refers to the height of the panel.

	Bricks are represented by the value of their length.  (ex. brick_1 is a 3" brick. brick_1 = 3)
	
	Rows have two representations in this program.  Initally rows are lists containing
	the bricks that make up the row in order.  (ex. [3,3,4.5,4.5] or [brick_1, brick_1, brick_2, brick_2])
	
	Later, rows are represented by tuples that contain the end positions of each brick (excluding the last one).
	This is to ease the process of determining if rows can be adjacent (if their edges line up) and so the rows
	can be stored as keys in dictionaries.  (ex. (3,6,10.5))
	(All rows start at a position of 0).
	
Usage:

	python brick_panel.py -ht [height of panel] -l [length of panel] -bl1 [length of brick_1] -bl2 [length of brick_2]
	
	height defaults to 10.
	length defaults to 48.
	brick_1 length defaults to 3.
	brick_2 length defaults to 4.5.
"""

import time
import argparse
import sys

def unique_permutations(t):
	"""Find all permutations of a list with repeating elements."""
	lt = list(t)
	lnt = len(lt)
	if lnt == 1:
		yield lt
	st = set(t)
	for d in st:
		lt.remove(d)
		for perm in unique_permutations(lt):
			yield [d]+perm
		lt.append(d)


def format_row(row):
	"""Change representation of rows to more easily check adjacency.
	
	Sums the lengths of bricks in row to find brick end points.  If two
	rows share the same end points, they can't be adjacent.
	  
	Example: (3,6,10.5) and (4.5,7.5,10.5) can't be adjacent because
	both have bricks that end at 10.5.  (All rows start at 0)
	"""
	# Example: format_row([3,4.5,3,4.5]) ==> (3,7.5,10.5)
	formatted_row = []
	# When comparing rows to see if edges line up, I don't want
	# to look at the total row length (since it will be the same for all rows).
	# This is why the last brick in the row is removed.
	row.pop()
	# Sum brick lengths in row.
	for brick in row:
		if formatted_row == []:
			formatted_row.append(brick)
		else:
			formatted_row.append(brick + formatted_row[-1])
	
	# Row needs to be a tuple (as opposed to list) so it can be a key in a dictionary.
	return tuple(formatted_row)
	
	
def build_all_rows(brick_1,brick_2,length):
	"""Find all possible rows of specified length made of brick_1 and brick_2."
	
	Determine the different quantities of the two lengths of bricks
	that can be used to make a row of a specified length.  Then
	find all the ways those bricks can be ordered to make unique rows.
	Change format of rows for easier adjacency comparison and return
	a list of rows.
	"""
	brick_quantity_1, brick_quantity_2 = 1, 0
	all_rows = []
	
	while brick_quantity_1 > 0:
		brick_quantity_1 = (length - brick_quantity_2*brick_2)/brick_1 
		if int(brick_quantity_1) == brick_quantity_1: 
			# Find all unique rows that can be made from x brick_1's and y brick_2's.
			all_rows += unique_permutations([brick_1]*int(brick_quantity_1) + \
											[brick_2]*int(brick_quantity_2))
		brick_quantity_2 += 1
	
	# Change the representation of rows.
	for index, row in enumerate(all_rows):
		all_rows[index] = format_row(row)
		
	return all_rows	


def build_adj_rows(input_row,brick_1,brick_2,length):
	"""Take row as input and return list of all rows that can be adjacent to it."""
	if input_row[0] == brick_1:
		current_rows = [[brick_2]]
	else:
		current_rows = [[brick_1]]
	next_rows = []
	while True:
		for row in current_rows:
			if row[-1] == length - brick_1 or row[-1] == length - brick_2:
				next_rows.append(row)
			else:
				add_brick_1 = row[-1] + brick_1
				add_brick_2 = row[-1] + brick_2
				if add_brick_1 not in input_row and add_brick_1 <= length:
					next_rows.append(row + [add_brick_1])
				if add_brick_2 not in input_row and add_brick_2 <= length:
					next_rows.append(row + [add_brick_2])
		if next_rows == current_rows:
			return [tuple(row) for row in next_rows]
		current_rows, next_rows = next_rows, []
	
	
def cache_adj_rows(all_rows,brick_1,brick_2,length):
	"""Save row and all rows that can be adjacent to it as key-value pairs."""
	adj_rows = {}
	for row in all_rows:
		adj_rows[row] = build_adj_rows(row,brick_1,brick_2,length)
	return adj_rows		


def calc_number_of_panels(run_args):
	"""Calculate and return number of panels of specified length and height
	that can be made from brick_1 and brick_2.
	"""
	all_rows = build_all_rows(run_args['brick length 1'],
							run_args['brick length 2'],
							run_args['length'],)
	adj_rows = cache_adj_rows(all_rows, run_args['brick length 1'],
							run_args['brick length 2'],
							run_args['length'],)					   
	current_lvl = {x:1 for x in adj_rows} 
	next_lvl = {}                           
	for x in range(run_args['height']-1): 
		for current_row, qty in current_lvl.items():  
			for next_row in adj_rows[current_row]:  
				if next_row in next_lvl:                  
					next_lvl[next_row] += qty              
				else:
					next_lvl[next_row] = qty               
		current_lvl, next_lvl = next_lvl, {}
	
	number_of_panels = sum([value for value in current_lvl.values()])
	
	return number_of_panels


def print_results(function, args):
	start = time.time()
	result = function(args)
	end = time.time()
	run_time = end - start
	
	print "Number of panels: %s" % result
	print "Run time: %0.2f" % run_time

	
def setup_args_parser():
	"""Defines valid command line arguments for brick_panel.py"""
	parser = argparse.ArgumentParser(description='Calculate number of panels')
	parser.add_argument('-bl1', action='store', dest='brick_1', 
    					default=3, type=float, help='Length of first brick.')
	parser.add_argument('-bl2', action='store', dest='brick_2',
    					default=4.5,type=float, help='Length of second brick.')
	parser.add_argument('-l', action='store', dest='length', default=48,
                        type=int, help='Length of brick panel.')
	parser.add_argument('-ht', action='store', dest='height', default=10,
                        type=int, help='Height of brick panel.')
	return parser.parse_args()


def verify_args(args):
	"""Checks if values input into brick_panel.py are valid.
	If so, returns a dictionary containing these values.
	"""
	run_args = {
				'brick length 1': args.brick_1,
				'brick length 2': args.brick_2,
				'length': args.length,
				'height': args.height
				}
	
	for arg in run_args:
		if run_args[arg] <= 0:
			print "Error: Negative or zero value entered for %s" % arg
			sys.exit(1)
			
	return run_args

if __name__ == '__main__':
	args = setup_args_parser()
	run_args = verify_args(args)
	print_results(calc_number_of_panels, run_args)
	
