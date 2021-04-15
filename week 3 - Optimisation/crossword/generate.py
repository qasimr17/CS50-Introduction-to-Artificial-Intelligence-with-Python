import sys
import copy 

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            self.domains[var] = set(val for val in self.domains[var] if len(val) == var.length)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        i, j = self.crossword.overlaps[x, y]
        revision = False 
        copy_domain = copy.deepcopy(self.domains)
        for x_val in copy_domain[x]:
            if not any(x_val[i] == y_val[j] for y_val in copy_domain[y]):
                revision = True 
                self.domains[x].remove(x_val)
        return revision

    def arcs_helper(self):
        """ Returns a list of all arcs (nodes that are connected)"""
        arcs_queue = []
        for var in self.domains:
            neighbours = self.crossword.neighbors(var)
            n = list((var, neighbour) for neighbour in neighbours)
            for arc in n:
                arcs_queue.append(arc)
        return arcs_queue

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            arcs = self.arcs_helper()
        
        while arcs:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False 
                for neighbour in self.crossword.neighbors(x) - {y}:
                    if (x, neighbour) not in arcs:
                        arcs.append((x, neighbour))
        return True 

        
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False 
        return True 
            

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # if self.assignment_complete(assignment):
        # check if all values are distinct 
        values = set(val for val in assignment.values()) 
        if len(values) != len(assignment):
            return False 
        
        # check if every value is the correct length
        for var, val in assignment.items():
            if var.length != len(val):
                return False 

        # check for any conflicts in neighbouring variables 
        for x in assignment:
            for y in assignment:
                if x != y:
                    overlap = self.crossword.overlaps[x, y]
                    if overlap:
                        i, j = overlap 
                        if assignment[x][i] != assignment[y][j]:
                            return False 
        return True 

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        if var not in assignment:
            least_constraining_values = {val: 0 for val in self.domains[var]}
            for neighbour in self.crossword.neighbors(var):
                if neighbour not in assignment:
                    i, j = self.crossword.overlaps[var, neighbour]
                    for x_val in self.domains[var]:
                        for y_val in self.domains[neighbour]:
                            if x_val[i] != y_val[j]:
                                least_constraining_values[x_val] += 1

        d_sort = dict(sorted(least_constraining_values.items(), key = lambda val: val[1]))
        return list(d_sort.keys())

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = []
        for var in self.domains:
            if var not in assignment:
                unassigned_vars.append(var)
        
        # first, sort by minimum remaining values in the domain
        min_remaining_value = sorted(unassigned_vars, key = lambda x: len(self.domains[x]))

        # Now keep those variables only who have tied, least number of mrv
        min_values = len(self.domains[min_remaining_value[0]])
        mrv = [var for var in min_remaining_value if len(self.domains[var]) == min_values]
        if len(mrv) > 0:
            highest_degrees = sorted(mrv, key = lambda x: len(self.crossword.neighbors(x)))
            return highest_degrees[0]
        else:
            return mrv[0]
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        assignment_copy = copy.deepcopy(assignment)
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment):
            assignment_copy[var] = val
            if self.consistent(assignment_copy):
                assignment[var] = val 
                result = self.backtrack(assignment)
                if self.assignment_complete(result):
                    return result 
            # assignment_copy[var] = None 
        return None 


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
