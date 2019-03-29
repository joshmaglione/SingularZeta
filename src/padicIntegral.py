#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

def _get_birat_map(vars1, vars2):
    strings = [str(x) for x in vars1]
    bi_dict = {strings[k] : vars2[k] for k in range(len(vars2))}
    return lambda x: bi_dict[str(x)]

def MapIntegrand(atlas, chart):
    birat_map = _get_birat_map(atlas.root.variables, chart.variables)
    return birat_map # TODO: comeback