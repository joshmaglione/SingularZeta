#
#   Copyright 2020 Joshua Maglione 
#
#   Distributed under MIT License
#


# A useful function for multiple lines
_cat_with_space = lambda x, y: x + "\n" + y

# Get the name of the atlas, which is the last folder of the directory.
def _get_atlas_name(A):
    direc = A.directory
    b = direc.rindex("/")
    if "/" in direc[:b]:
        a = direc[:b].rindex("/")
    else:
        a = -1
    return direc[a + 1:b]

# The preamble to the tex document containing all the stuff above 
# "\begin{document}."
def _preamble(title=None, author=None):
    lines = [
        "\\documentclass[a4paper]{amsart}\n",
        "\\usepackage{enumerate}",
        "\\usepackage{hyperref}",
        "\\hypersetup{",
        "\tcolorlinks=true,",
        "\tlinkcolor=blue,",
        "\tfilecolor=blue,",
        "\turlcolor=blue,",
        "\tcitecolor=blue,",
        "}",
        "\\usepackage{amsmath}",
        "\\usepackage{amsthm}",
        "\\usepackage{amssymb}",
        "\\usepackage{mathpazo}",
        "\\usepackage{url}",
        "\\usepackage[labelformat=simple]{subcaption}",
        "\\usepackage{tikz}",
        "\\usepackage{pgf}",
        "\\usepackage{longtable}",
        "\\usepackage{multirow}",
        "\\usepackage{graphicx}\n",
        "\\title{%s}" % (title),
        "\\author{%s}" % (author),
        "\\date{\\today}"
    ]
    return reduce(_cat_with_space, lines)
    
# The introduction of the tex document. 
def _intro(direc):
    sing_zeta = "\\textsf{SingularZeta}"
    direc_str = "\\texttt{%s}" % (direc)
    Fp = "$\\mathbb{F}_p$"
    intro = """
        This is a report generated by %s concerning the chart data in the 
        directory %s. We report all the computations we undertake in computing 
        the cone integral associated to %s. While this report is being 
        developed, we provide the table of varieties containing the varieties 
        for which we need to count the number of %s-rational points. These 
        cannot be done automatically with the current implementation of %s. At 
        the end, we list all the varieties and their number of %s-points. 
        Special attention should be given to the ones with no %s-points. 
    """ % (
        sing_zeta, 
        direc_str,
        direc_str,
        Fp, 
        sing_zeta,
        Fp,
        Fp
    )
    return intro.replace("        ", "")

# Given a set of integers, return a latex compatible string for a set of 
# integers.
def _set_to_latex(S):
    content = reduce(lambda x, y: x + str(y) + ", ", S, "")
    return "$\\{" + content[:-2] + "\\}$"

# Format a polynomial to a latex compatible string.
def _format_poly(f):
    from sage.all import latex
    return "$%s$" % (latex(f))

# Convert a tuple of a polynomial ring and a list of polynomials into latex 
# output.
def _poly_data_to_latex(P):
    from sage.all import latex
    system = P[1]
    gens = P[0].gens()
    def _format_system(S):
        poly_sys = "$\\begin{array}{c} "
        sys_str = map(lambda f: latex(f), S)
        poly_sys = reduce(lambda x, y: x + y + "\\\\ ", sys_str, poly_sys)
        return poly_sys[:-3] + " \\end{array}$"
    if len(system) <= 1:
        return _format_poly(system[0]), len(gens)
    else:
        return _format_system(system), len(gens)

# A function to build the entire F_p-table as a latex compatible string.
def _build_Fp_table(A):
    Fp = "$\\mathbb{F}_p$"
    table_top = [
        "\\begin{center}",
        "\t\\begin{longtable}{c|c|c|c|c|c}",
        "\t\tChart & Vertex & Variety & Dim.\\ & %s-points\\\\ \\hline \\hline" % (Fp),
    ]
    table_end = [
        "\t\\end{longtable}",
        "\\end{center}"
    ]

    # The main function we apply to all charts.
    def extraction(C):
        ID = C._id
        V = C.intLat.vertices
        Fp = C.intLat.pRationalPoints()
        data = zip(V, Fp)
        chart_header = ["\t\t\\multirow{%s}{*}{%s}" % (len(V), ID)]

        def get_info(X):
            info = "\t\t\t%s & " % (_set_to_latex(X[0]))
            info += "%s & %s & " % (_poly_data_to_latex(X[1][1]))
            if not "C" in str(X[1][0]):
                info += _format_poly(X[1][0])
            info += " \\\\"
            return info

        chart_section = map(get_info, data)
        chart_section[-1] = chart_section[-1] + " \\hline"
        return chart_header + chart_section

    # Get all the chart data from extraction, and flatten it down.
    table_main = reduce(lambda x, y: x + y, map(extraction, A.charts))
    # Put everything together and return a string.
    table = table_top + table_main + table_end
    return reduce(_cat_with_space, table)


# ==============================================================================
#   Main function
# ==============================================================================

# The following is a function that outputs a tex file. The tex file provides 
# information concerning the polynomials associated to the atlas A for which we 
# cannot automatically determine the number of F_p-rational points. 
def PolynomialReport(A, file=""): 
    # Take care of input
    if not isinstance(file, str):
        raise TypeError("Expected 'file' to be a string.")

    # Make sure the file string is formatted correctly.
    atlas_name = _get_atlas_name(A)
    if file == "":
        file = atlas_name + "Report.tex"
    if not ".tex" in file:
        file_name = file + ".tex"
    else:
        file_name = file
    atlas_name_latex = atlas_name.replace("_", "\\_")

    title = "Report for %s" % (atlas_name_latex)
    with open(file_name, 'w') as tex_file:
        tex_file.write(_preamble(title=title))
        tex_file.write("\n\n\\begin{document}")
        tex_file.write("\n\n\\maketitle")
        tex_file.write("\n\\tableofcontents\n\n")
        tex_file.write(_intro(atlas_name_latex))
    
    # Determine the F_p-rational points of the atlas. 
    # These are stored with the intersection lattices.
    _ = map(lambda C: C.intLat.pRationalPoints(user_input=False), A.charts)
    table = _build_Fp_table(A)
    with open(file_name, 'a') as tex_file:
        tex_file.write("\n\n" + table + "\n\n")

    with open(file_name, 'a') as tex_file:
        tex_file.write("\n\n\\end{document}")

    return 