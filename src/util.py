#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

def _my_odom(max_vals):
    curr = [0 for k in max_vals]
    while curr[-1] <= max_vals[-1]:
        yield curr
        curr[0] += 1
        for k in range(len(max_vals) - 1):
            if curr[k] > max_vals[k]:
                curr[k] = 0
                curr[k + 1] += 1
    