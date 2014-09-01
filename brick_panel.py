import time

def unique_permutations(t):
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
	
	
def build_all_rows(bl1,bl2,l):
	bq1, bq2 = 1, 0
	all_rows = []
	while bq1 > 0:
		bq1 = (l - bq2*bl2)/bl1  
		if int(bq1) == bq1:    
			all_rows += unique_permutations([bl1]*int(bq1) + [bl2]*int(bq2))
		bq2 += 1
	
	return all_rows	
	
	
def build_adj_rows(row,bl1,bl2,l):
	current_brick = [[z for z in [bl1,bl2] if z not in row]]
	next_brick = []
	while True:
		for x in current_brick:
			if x[-1] == l:
				next_brick.append(x)
			else:
				a = x[-1] + bl1
				b = x[-1] + bl2
				if a not in row and a <= l:
					next_brick.append(x + [a])
				if b not in row and b <= l:
					next_brick.append(x + [b])
		if next_brick == current_brick:
			return [tuple(y[:len(y)-1]) for y in next_brick]
		current_brick, next_brick = next_brick, []
	
	
def cache_adj_rows(all_rows,bl1,bl2,l):
	adj_rows = {}
	for row in all_rows:
		new_row = tuple([sum(row[:x]) for x in range(1,len(row))])
		adj_rows[new_row] = build_adj_rows(new_row,bl1,bl2,l)
	return adj_rows		


def calc_number_of_panels(bl1=3,bl2=4.5,l=48,h=10):	
	all_rows = build_all_rows(bl1,bl2,l)							   
	adj_rows = cache_adj_rows(all_rows,bl1,bl2,l)
	current_lvl = {x:1 for x in adj_rows} 
	next_lvl = {}                           
	for x in range(h-1): 
		for current_row, qty in current_lvl.items():  
			for next_row in adj_rows[current_row]:  
				if next_row in next_lvl:                  
					next_lvl[next_row] += qty              
				else:
					next_lvl[next_row] = qty               
		current_lvl, next_lvl = next_lvl, {}

	return sum([value for value in current_lvl.values()])

if __name__ == '__main__':
	start = time.time()
	number_of_panels = calc_number_of_panels()
	print "Number of possible brick panels: %s" % number_of_panels
	end = time.time()
	run_time = end - start
	print "Run time: %.2f s" % run_time



	
		
