import itertools
import random
import copy 


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)
        return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        return set() 

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            return 1 # return statements to keep track of number of sentences updated by each cell 
        return 0

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            return 1 
        return 0 


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        counter = 0
        self.mines.add(cell)
        for sentence in self.knowledge:
            counter += sentence.mark_mine(cell)
        return counter # this returns the actual number of sentences updated by a particular cell 

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        counter = 0 
        self.safes.add(cell)
        for sentence in self.knowledge:
            counter += sentence.mark_safe(cell)
        return counter 

    # helper function that returns the set of all possible neighbors of a particular cell:
    def cell_neighbors(self, cell):
        
        neighbors = set()
        for height in range(cell[0]-1, cell[0]+2):
            for width in range(cell[1]-1, cell[1]+2):
                if (height, width) == cell:
                    continue
                    
                if height >= 0 and height < self.height:
                    if width >= 0 and width < self.width:
                        neighbors.add((height, width))
        print("Neighbours are: ", neighbors)
        return neighbors

    # helper to add sentences to knowledge base, based on value of cell and count
    def add_sentences(self, cells, count):

        count_to_add = copy.deepcopy(count) 
        cells_to_add = set() 
        for cell in cells:
            if cell in self.mines:
                count_to_add -= 1
                continue
            elif cell in self.safes:
                continue
            cells_to_add.add(cell)
        
        return cells_to_add, count_to_add

    # helper for updating KB based on subset inference:
    def subset_update(self):

        new_inferences = []
        removals = []

        for sentence1 in self.knowledge:
            if not sentence1.cells:
                removals.append(sentence1)
                continue
            
            for sentence2 in self.knowledge:
                if not sentence2.cells:
                    removals.append(sentence2)
                    continue
                    
                if sentence1 != sentence2:
                    if sentence1.cells.issubset(sentence2.cells):
                        cells_to_add = sentence2.cells.difference(sentence1.cells)
                        count_to_add = sentence2.count - sentence1.count 
                        new_inference_to_add = Sentence(cells_to_add, count_to_add)
                        if new_inference_to_add not in self.knowledge:
                            new_inferences.append(new_inference_to_add)
        self.knowledge = [sent for sent in self.knowledge if sent not in removals]
        return new_inferences

    def update_cells(self):

        # this will repeat the update if any update was made in the previous cycle
        counter = 1
        while counter:
            counter = 0
            for sentence in self.knowledge:
                for cell in sentence.known_safes():
                    # this loop will run as long as there are known safes in the sentences kept in our KB
                    # but realize that we need to keep only those sentences/cells in our KB whose state we are not yet certain of 
                    # therefore every time there is a known safe/mine, we update our sentences (remove the known safes from there)
                    self.mark_safe(cell)
                    counter += 1
                for cell in sentence.known_mines():
                    # if cell not in self.mines:
                    self.mark_mine(cell)
                    counter += 1
            
            # similar logic applied here as well
            # for each known cell, we update our sentences accordingly
            for cell in self.safes:
                counter += self.mark_safe(cell)
            for cell in self.mines:
                counter += self.mark_mine(cell)


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark cell as move made
        self.moves_made.add(cell)

        # mark cell as safe 
        self.mark_safe(cell)

        # add a new sentence to AI's KB (only adding those cells whose values haven't already been determined)
        neighbors = self.cell_neighbors(cell)
        cells_to_add, count_to_add = self.add_sentences(neighbors, count)
        if cells_to_add:
            new_sentence = Sentence(cells_to_add, count_to_add)
            self.knowledge.append(new_sentence)

        # update cells as mines/safes:
        self.update_cells()


        # inference based on subset method 
        new_inferences = self.subset_update()

        while new_inferences:
            for sentence in new_inferences:
                self.knowledge.append(sentence)
            self.update_cells()
            new_inferences = self.subset_update()



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made and move not in self.mines:
                return move 
        return None 
            

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if move not in self.moves_made and move not in self.mines:
                    return move 
        
        return None 




