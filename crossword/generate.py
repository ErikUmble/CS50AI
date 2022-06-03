import sys
from queue import Queue

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

        for var, elements in list(self.domains.items()):
            for element in list(elements):
                if len(element) != var.length:
                    self.domains[var].remove(element)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        overlap = self.crossword.overlaps[x, y]

        if not overlap:
            return False

        for possible_word in list(self.domains[x]):
            possible = False
            for possible_y_word in self.domains[y]:
                if possible_word[overlap[0]] == possible_y_word[overlap[1]]:
                    possible = True
                    break

            if not possible:
                self.domains[x].remove(possible_word)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = Queue()
        if arcs is None:
            for var_par in self.crossword.overlaps:
                if var_par is not None:
                    queue.put(var_par)
        else:
            for var_par in arcs:
                queue.put(var_par)
                
        while not queue.empty():
            x, y = queue.get()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x):
                    if not neighbor == y:
                        queue.put((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var, word in assignment.items():
            if word is not None:
                if len(word) != var.length:
                    return False
                for y, y_word in assignment.items():
                    if y_word is not None:
                        if var != y:
                            if word == y_word:
                                return False
                            overlap = self.crossword.overlaps[var, y]
                            if overlap is not None:
                                if word[overlap[0]] != y_word[overlap[1]]:
                                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain_values = {}
        for domain_value in self.domains[var]:
            num_eliminated = 0
            for other_var in self.crossword.variables:

                if other_var not in assignment and other_var != var:
                    overlap = self.crossword.overlaps[var, other_var]
                    if overlap is not None:

                        # See if the domain value is allowed with the overlap
                        for other_var_possible_value in self.domains[other_var]:
                            if domain_value[overlap[0]] != other_var_possible_value[overlap[1]]:
                                num_eliminated += 1
            domain_values[domain_value] = num_eliminated

        # Convert into a sorted list based on the number of eliminations that each value causes
        domain_values = sorted(domain_values, key=lambda value: domain_values[value])
        return domain_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        smallest_domain = 10000000000  # Initialize at a very high number so that any variable will be lower
        current_best = []

        for var in self.crossword.variables:
            if var not in assignment:
                domain_size = len(self.domains[var])
                if domain_size < smallest_domain:
                    smallest_domain = domain_size
                    current_best = [var]
                elif domain_size == smallest_domain:
                    current_best.append(var)

        if len(current_best) == 0:
            # Assignment must be complete
            return None
        elif len(current_best) == 1:
            return current_best[0]
        else:
            # Multiple variables have the same smallest domain size
            # So find degree by the number of neighbors and return the var with highest degree
            degrees = {}
            for var in current_best:
                degrees[var] = len(self.crossword.neighbors(var))
            return sorted(degrees, key=lambda var: degrees[var], reverse=True)[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for possible_word in self.order_domain_values(var, assignment):

            assignment[var] = possible_word
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]
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
