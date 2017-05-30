def num_generator_yield(max):
	num = 1
	while num <= max:
		yield num ** 2
		num += 1
		

for val in num_generator_yield(4):
    print(val)

# out:
# 	1
# 	4
# 	9
# 	16 