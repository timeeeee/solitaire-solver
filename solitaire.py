"""
cards represented by tuple of two integers:
(suit, rank)
where suit is in (0, 3) and rank is in (0, 12)

suits are (spades, diamonds, clubs, hearts) so that evens are black and odds
are red.

IN GENERAL when a list represents a stack of cards, the cards at the END of the
list are the most readily accessible in a real-world game of solitaire- the end
of a list in this script corresponds to the physical top of a stack of cards,
whether they're face up or face down. This means that "pop" means "take a card
from the top of a real-world stack" and "append" means "put a card physically
on top of a stack". 
"""

from copy import deepcopy
from random import shuffle


SUITS = ["Spades", "Diamonds", "Clubs", "Hearts"]
RANKS = [
    "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen",
    "King"]

# Once we've solved a particular state, cache the solution
# Is this going to get huge?!
# Will this be helpful?
CACHE = dict()
CACHE_HITS = 0


class Card(object):
    def __init__(self, rank, suit):
        """
        Suit and rank are integers!
        """
        self.suit = suit
        self.rank = rank
        
    def fits_under(self, over):
        different_colors = bool((self.suit - over.suit) % 2)
        sequential = (over.rank - self.rank == 1)
        return (different_colors and sequential)

    def __repr__(self):
        return "Card({}, {})".format(self.rank, self.suit)

    def __str__(self):
        return "{} of {}".format(RANKS[self.rank], SUITS[self.suit])

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return (self.suit, self.rank)


DECK = [Card(rank, suit) for suit in range(4) for rank in range(13)]


class InvalidMove(RuntimeError):
    pass


class GameState(object):
    """
    Represents the state of 4 areas the cards can be in:

    Stock: The upside-down cards a player can draw 3 at a time from. This is a
      list, and Cards are pulled from the *end* of this- the first card in the
      list corresponds to the physical bottom card in a real game of solitaire,
      and the last card corresponds to the physical top card.

    Waste: The upside-up cards a player can use the top card of. Again, the
      available cards are at the end of this list- the last card is the
      accessible one.

    Foundation: The cards that have been successfully sorted by number and
      suit- once the foundation is full the game is won. This is a 4-tuple,
      representing how many cards of each suit are that suit's stack.

    Tableau: The cards which are currently in play. In the physical game there
      are 7 columns, each with a stack of upside down cards at the top and
      visible columns descending. self.tableau is a list of columns, and each
      column contains two lists, a list of face-down cards and a list of
      face-up cards. In both cases the most readily available cards are at the
      end of the list.
    """
    def __init__(self, deck):
        # Deal tableau of 7 columns, with 1..7 cards. Each column consists of
        # two lists, upside-down cards and upside-up ones.
        # The rest go into the "stock". The waste is an initially empty list.
        # The foundations begin as a list of 4 zeros, how many cards they have.
        deck = deck.copy()

        self.tableau = [[list(), list()] for _ in range(7)]
        for i in range(7):
            # deal face-down cards
            for row in range(i):
                self.tableau[i][0].append(deck.pop())

            # ... and one face-up
            self.tableau[i][1].append(deck.pop())

        # put the rest in the stock
        self.stock = deck  # just use reference to deck since we copied it
        self.waste = []

        # counts, how many cards are in each stack of the foundation
        self.foundation = [0, 0, 0, 0]

    def __str__(self):
        output = "MOST READILY AVAILABLE CARDS ('TOP') AT END OF EACH LIST\n"
        output += "stock: {}\n".format(self.stock)
        output += "waste: {}\n".format(self.waste)
        output += "foundation:\n"
        for index, col in enumerate(self.foundation):
            output += "    col {}: {}\n".format(index, col)

        output += "tableau:\n"
        for index, col in enumerate(self.tableau):
            output += "    col {}: {}\n".format(index, col)

        return output

    def valid_moves(self):
        """
        Return a list of Move objects representing all possible moves in the
        current game state!

        possible moves:
        - TurnStock(): If the stock pile is empty, move the waste pile onto the
          stock pile. Flip up to three cards from the stock pile onto the waste
          pile. This is always possible (could make impossible if stock and
          waste are both empty? but applying it in that case will result in an
          unchanged game state which will be rejected as "visited")
        - MoveTableauToTableau(source_col, source_row, target_col)
        - MoveTableauToFoundation(source_col)
        - MoveWasteToTableau(target_col)
        - MoveWasteToFoundation()
        - MoveFoundationToTableau(source_col, target_col)
        """
        moves = []

        print(self)

        # move tableau to foundation?
        for col in range(7):
            if len(self.tableau[col][1]) == 0:
                continue

            card = self.tableau[col][1][-1]
            if card.rank == self.foundation[card.suit]:
                moves.append(MoveTableauToFoundation(col))

        # move waste to foundation?
        if len(self.waste) > 0:
            card = self.waste[-1]
            if card.rank == self.foundation[card.suit]:
                moves.append(MoveWasteToFoundation())

        # move tableau to tableau?
        for col in range(7):
            for row in range(len(self.tableau[col][1])):
                for target_col in range(7):
                    if target_col == col:
                        continue

                    top_card = self.tableau[col][1][row]

                    # is the target column empty?
                    if len(self.tableau[target_col][1]) == 0:
                        # a king could go here
                        if top_card.rank == 12:
                            moves.append(MoveTableauToTableau(col, row, target_col))
                    else:
                        other_card = self.tableau[target_col][1][-1]
                        if top_card.fits_under(other_card):
                            moves.append(MoveTableauToTableau(col, row, target_col))

        # move waste to tableau?
        if len(self.waste) > 0:
            card = self.waste[-1]
            for target_col in range(7):
                # is the target column empty?
                if len(self.tableau[target_col][1]) == 0:
                    # only a king can go here
                    if card.rank == 12:
                        moves.append(MoveWasteToTableau(target_col))
                elif card.fits_under(self.tableau[target_col][1][-1]):
                    moves.append(MoveWasteToTableau(target_col))

        # move foundation to tableau?
        for suit in range(4):
            # can't do this if there are no cards
            if self.foundation[suit] == 0:
                continue
            
            for target_col in range(7):
                card = Card(self.foundation[suit] - 1, suit)
                if len(self.tableau[target_col][1]) == 0:
                    if card.rank == 12:
                        moves.append(MoveFoundationToTableau(suit, target_col))
                elif card.fits_under(self.tableau[target_col][1][-1]):
                    moves.append(MoveFoundationToTableau(suit, target_col))

        # turn stock
        moves.append(TurnStock())

        return moves

    def turn_stock(self):
        new_state = deepcopy(self)

        # Do we need to move the waste pile back onto the stock?
        if len(new_state.stock) == 0:
            new_state.stock = list(reversed(new_state.waste))
            new_state.waste = []

        # move up to three cards from the stock onto the waste pile
        for _ in range(min(3, len(new_state.stock))):
            new_state.waste.append(new_state.stock.pop())

        return new_state

    def move_tableau_to_tableau(self, source_col, source_row, target_col):
        # check: can we move this stack there?
        try:
            under = self.tableau[source_col][1][source_row]
        except IndexError:
            raise InvalidMove(
                "There's no cards in column {}".format(source_col))
        
        try:
            over = self.tableau[target_col][1][-1]
            if not under.fits_under(over):
                raise InvalidMove("{} doesn't fit under {} in the tableau!".format(
                    str(under), str(over)))
        except IndexError:
            # if the target column is empty, OK if the source is a King
            if under.rank != 12:
                raise InvalidMove("Only Kings can be moved to empty columns")

        new_state = deepcopy(self)

        # add to new column
        cards_to_move = new_state.tableau[source_col][1][source_row:]
        new_state.tableau[target_col][1].extend(cards_to_move)

        # remove from old column
        cards_left = new_state.tableau[source_col][1][:source_row]
        new_state.tableau[source_col][1] = cards_left

        # if source column is now empty, we can flip a card
        if len(new_state.tableau[source_col][1]) == 0:
            if len(new_state.tableau[source_col][0]) > 0:
                flipped = new_state.tableau[source_col][0].pop()
                new_state.tableau[source_col][1].append(flipped)

        return new_state

    def move_tableau_to_foundation(self, source_col):
        card = self.tableau[source_col][1][-1]

        # check: can this card fit on the foundation?
        if self.foundation[card.suit] < card.rank:
            raise InvalidMove("{} foundation only goes up to {}".format(
                card.suit, self.foundation[card.suit]))

        new_state = deepcopy(self)

        # remove the card from the tableau
        new_state.tableau[source_col][1].pop()

        # increment this cards suit in the foundation
        new_state.foundation[card.suit] += 1

        # flip a new card over in the tableau if it just got exposed
        if len(new_state.tableau[source_col][1]) == 0:
            if len(new_state.tableau[source_col][0]) > 0:
                flipped = new_state.tableau[source_col][0].pop()
                new_state.tableau[source_col][1].append(flipped)

        return new_state

    def move_waste_to_tableau(self, target_col):
        # is there a card available in the waste?
        if len(self.waste) == 0:
            raise InvalidMove("The waste is empty")

        under = self.waste[-1]
        
        try:
            over = self.tableau[target_col][1][-1]
            if not under.fits_under(over):
                raise InvalidMove("{} doesn't fit under {} in the tableau!".format(
                    str(under), str(over)))
        except IndexError:
            # if the target column is empty, OK if the source is a King
            if under.rank != 12:
                raise InvalidMove("Only Kings can be moved to empty columns")

        new_state = deepcopy(self)        

        # pop from the waste
        card = new_state.waste.pop()

        # put it in the tableau
        new_state.tableau[target_col][1].append(card)

        return new_state

    def move_foundation_to_tableau(self, source_suit, target_col):
        # is there a card here?
        if self.foundation[source_suit] == 0:
            raise InvalidMove(
                "There is nothing in the foundation for {}".format(
                    SUITS[source_suit]))

        card = Card(self.foundation[source_suit] - 1, source_suit)

        # does this card fit in the tableau?
        try:
            over = self.tableau[target_col][1][-1]
            if not card.fits_under(over):
                raise InvalidMove("{} doesn't fit under {} in the tableau!".format(
                    str(card), str(over)))
        except IndexError:
            # if the target column is empty, OK if the source is a King
            if card.rank != 12:
                raise InvalidMove("Only Kings can be moved to empty columns")

        new_state = deepcopy(self)

        # remove it from the foundation
        foundation[source_suit] -= 1

        # put it in the tableau
        tableau[target_col][1].append(card)

        return new_state

    def move_waste_to_foundation(self):
        new_state = deepcopy(self)

        if len(new_state.waste) == 0:
            raise InvalidMove

        # does this card fit on the foundation for its suit?
        card = new_state.waste[-1]
        if card.rank != new_state.foundation[card.suit]:
            raise InvalidMove

        new_state.waste.pop()
        new_state.foundation[card.suit] += 1
        return new_state

    def apply_move(self, move):
        """
        Applying a move does not modify the current game state (!) and returns
        a new GameState object representing the result of the move, or raises
        an error if the move was not possible.
        """
        if isinstance(move, TurnStock):
            return self.turn_stock()
        elif isinstance(move, MoveTableauToFoundation):
            return self.move_tableau_to_foundation(move.source_col)
        elif isinstance(move, MoveTableauToTableau):
            return self.move_tableau_to_tableau(
                move.source_col, move.source_row, move.target_col)
        elif isinstance(move, MoveWasteToFoundation):
            return self.move_waste_to_foundation()
        elif isinstance(move, MoveWasteToTableau):
            return self.move_waste_to_tableau(move.target_col)
        elif isinstance(move, MoveFoundationToTableau):
            return self.move_foundation_to_tableau(
                move.source_col, move.target_col)
        else:
            raise InvalidMove(
                'GameState.apply_move does not know how to do "{}"'.format(
                    move))

    def is_won(self):
        return (self.foundation == [13, 13, 13, 13])

    def __hash__(self):
        raise NotImplementedError

    def __eq__(self, other_game_state):
        return hash(self) == hash(other_game_state)


class Move(object):
    """
    Useless Parent class for moves

    Moves won't do shit, except remember source and target columns, if
    needed for that type of move.
    """
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError


class TurnStock(Move):
    """
    This class represents moving (up to) 3 cards from the stock to waste,
    recycling all cards from the waste to the stock first if necessary.
    """
    def __eq__(self, other):
        return isinstance(other, TurnStock)

    def __hash__(self):
        return 0

    def __repr__(self):
        return "TurnStock()"


class MoveTableauToTableau(Move):
    """
    Move a card or stack of cards from one column of the tableau to another.
    """
    def __init__(self, source_col, source_row, target_col):
        self.source_col = source_col
        self.source_row = source_row
        self.target_col = target_col

    def __hash__(self):
        return hash((self.source_col, self.source_row, self.target_col))

    def __eq__(self, other):
        return (
            isinstance(other, MoveTableauToTableau)
            and hash(self) == hash(other))

    def __repr__(self):
        return "MoveTableauToTableau({}, {}, {})".format(
            self.source_col, self.source_row, self.target_col)


class MoveTableauToFoundation(Move):
    """
    Move a card from the tableau onto a foundation.
    """
    def __init__(self, source_col):
        self.source_col = source_col

    def __hash__(self):
        return self.source_col

    def __eq__(self, other):
        return (
            isinstance(other, MoveTableauToFoundation)
            and hash(self) == hash(other))

    def __repr__(self):
        return "MoveTableauToFoundation({})".format(self.source_col)


class MoveWasteToTableau(Move):
    """
    Move the last waste card to the tableau.
    """
    def __init__(self, target_col):
        self.target_col = target_col

    def __hash__(self):
        return self.target_col

    def __eq__(self, other):
        return (
            isinstance(other, MoveWasteToTableau)
            and hash(self) == hash(other))

    def __repr__(self):
        return "MoveWasteToTableau({})".format(self.target_col)


class MoveWasteToFoundation(Move):
    """
    Move the last waste card onto the foundation.

    We don't need to know anything because there's only one card accessible in
    the waste, and depending on its suit there will be only one place it can
    go in the foundation.
    """
    def __init__(self):
        pass

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return isinstance(other, MoveWasteToFoundation)

    def __repr__(self):
        return "MoveWasteToFoundation()"


class MoveFoundationToTableau(Move):
    """
    Move a card from the foundation to the tableau
    """
    def __init__(self, source_col, target_col):
        self.source_col = source_col
        self.target_col = target_col

    def __hash__(self):
        return hash((self.source_col, self.target_col))

    def __eq__(self, other):
        return (
            isinstance(other, MoveFoundationToTableau)
            and hash(self) == hash(other))

    def __repr__(self):
        return "MoveFoundationToTableau({}, {})".format(
            self.source_col, self.target_col)


def deal_random_game():
    deck = deepcopy(DECK)
    shuffle(deck)
    return GameState(deck)


def solve(game_state, visited=None):
    """
    Return a sequence of moves that solves the game, or None if there is no
    solution.
    """
    global CACHE, CACHE_HITS
    
    if game_state in CACHE:
        CACHE_HITS += 1
        return CACHE[game_state]

    # if this is a new game, start tracking what game states we've tried
    if visited == None:
        visited = set()

    # If we've already been to this game state up a number of frames of
    # recursion, don't bother (but also don't cache this as a loss)
    if game_state in visited:
        return None

    # Otherwise: we haven't tried this game state until just now. Mark it as
    # visited before trying to solve from here.
    visited.add(game_state)
    
    # base case: game is won. No moves necessary!
    if game_state.is_won():
        CACHE[game_state] = []
        return []

    for move in game_state.valid_moves():
        rest_of_moves = solve(game_state.apply_move(move), visited)
        if rest_of_moves is not None:
            solution = [move] + rest_of_moves
            CACHE[game_state] = solution
            return solution

    # if we get here, we did not find a way to win this game!
    CACHE[game_state] = None
    return None
