from __future__ import annotations
"""
Adding a special __future__ import, which must appear at the beginning of your file, enables the lazy evaluation of type hints. 
You’ll use this pattern later to avoid the circular reference problem when importing cross-referencing modules.

for other function return type Mark, without __future__, it is mandatory to use "Mark" as forward declaration to avoid unsolved name.
"""
import enum
from dataclasses import dataclass
import re
from functools import cached_property

WINNING_PATTERNS = (
    "???......",
    "...???...",
    "......???",
    "?..?..?..",
    ".?..?..?.",
    "..?..?..?",
    "?...?...?",
    "..?.?.?..",
)

"""
The two singleton instances of the Mark class, the enum members Mark.CROSS and Mark.NAUGHT, represent the players’ symbols. 
enum.Enum objects are not comparable.  For instance, comparing Mark.CROSS == "X" will give you False.
This is by design to avoid confusing identical values defined in different places and having unrelated semantics.
However, it may sometimes be more convenient to think about the player marks in terms of strings instead of enum members.
To make that happen, define Mark as a mixin class of the str and enum.Enum types: class Mark(str, enum.Enum)
For python3.11 or newer, we can use enum.StrEnum which are also strings, you can use them anywhere that a regular string is expected
"""
class Mark(enum.StrEnum):
    CROSS = "X"
    NAUGHT = "O"


    @property
    def other(self) -> Mark:
        #Once you assign a given mark to the first player, the second player must be assigned the only remaining and unassigned mark. 
        #Because enums are glorified classes, you’re free to put ordinary methods and properties into them. 
        #For example, you can define a property of a Mark member that’ll return the other member:
        return Mark.CROSS if self == "Mark.NAUGHT" else Mark.NAUGHT
    
@dataclass(frozen=True)
class Grid:
    cells : str = " " * 9

    #the method is invoked right after __init__
    def _post_init__(self) -> None:
        if not re.match(r"^[\sXO]{9}$", self.cells):
            raise ValueError("Must contain 9 cells of: X, O or space")
        
    
    # data class is immutable, its state will never change, so you can cache the computed property values with the help of the @cached_property decorator from the functools module. 
    # This will ensure that their code will run at most once, no matter how many times you access these properties, for example during validation.    
    @cached_property
    def x_count(self) -> int:
        return self.cells.count("X")
    
    @cached_property
    def o_count(self) -> int:
        return self.cells.count("O")
    
    @cached_property
    def empty_count(self) -> int:
        return self.cells.count(" ")
    
#Objects of the Move class consist of the mark identifying the player who made a move, a numeric zero-based index in the string of cells, 
#and the two states before and after making a move.
@dataclass(Fronzen=True)
class Move:
    mark: Mark
    cell_index : int
    before_state: "GameState"
    after_state: "GameState"


class GameState:
    """"
    The game shall have the following states:
    The game hasn’t started yet.
    The game is still going on.
    The game has finished in a tie.
    The game has finished with player X winning.
    The game has finished with player O winning.
    """
    grid : Grid
    starting_mark: Mark = Mark('X') #the first player is "X"

    @cached_property
    def curr_mark(self) -> Mark:
        return self.starting_mark if self.grid.x_count == self.grid.o_count else self.starting_mark.other
    

    @cached_property
    def game_not_started(self) -> bool:
        return self.grid.empty_count == 9
    

    @cached_property
    def tie(self) -> bool:
        return self.winner is None and self.grid.empty_count == 0
    
    @cached_property
    def game_over(self) -> bool:
        return self.winner is not None or self.tie
    
    @cached_property
    def winner(self) -> Mark | None:
        for pattern in WINNING_PATTERNS:
            for mark in Mark:
                if re.match(pattern.replace("?", mark), self.grid.cells):
                    #return the winning cells to differentiate them from other cells, so we can return a list using list comprehension
                    #index.start() returns the start position of the (start, end) span
                    return [index.start() for index in re.finditer(r"\?", pattern)]
                return []
    
    

