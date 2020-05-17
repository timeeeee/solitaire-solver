from nose.tools import *

from solitaire import *


# visible cards in example state are, from left to right:
# King of Hearts
# Jack of Hearts
# 8 of Hearts
# 3 of Hearts
# Queen of Clubs
# 6 of Clubs
# Queen of Diamonds
example_state_1 = GameState(DECK)


def test_does_fit_under():
    for black_suit in [0, 2]:
        for red_suit in [1, 3]:
            for under_rank in range(12):
                # with black suit on top
                under = Card(under_rank, red_suit)
                over = Card(under_rank + 1, black_suit)
                assert_true(under.fits_under(over))

                # with red suit on top
                under = Card(under_rank, black_suit)
                over = Card(under_rank + 1, red_suit)
                assert_true(under.fits_under(over))


def test_same_color_does_not_fit_under():
    for under_suit in range(3):
        for under_rank in range(12):
            under = Card(under_rank, under_suit)
            over = Card(under_rank + 1, under_suit)
            assert_false(under.fits_under(over))

            # different suit:
            over_suit = (under_suit + 2) % 4
            over = Card(under_rank + 1, over_suit)
            assert_false(under.fits_under(over))


def test_non_sequential_does_not_fit_under():
    for black_suit in [0, 2]:
        for red_suit in [1, 3]:
            for under_rank in range(13):
                for over_rank in range(13):
                    # skip if sequential
                    if over_rank == under_rank + 1:
                        continue

                    # red on top:
                    under = Card(under_rank, black_suit)
                    over = Card(over_rank, red_suit)
                    assert_false(under.fits_under(over))

                    # black on top:
                    under = Card(under_rank, red_suit)
                    over = Card(over_rank, black_suit)
                    assert_false(under.fits_under(over))


def test_is_won():
    state = GameState(DECK)
    state.foundation[0] = 13
    state.foundation[1] = 13
    state.foundation[2] = 13
    state.foundation[3] = 13
    assert_true(state.is_won())


def test_card_repr():
    for suit_n, suit_str in enumerate(SUITS):
        for rank_n, rank_str in enumerate(RANKS):
            card = Card(rank_n, suit_n)
            expected = 'Card({}, {})'.format(rank_n, suit_n)
            assert_equal(repr(card), expected)


def test_card_str():
    for suit_n, suit_str in enumerate(SUITS):
        for rank_n, rank_str in enumerate(RANKS):
            card = Card(rank_n, suit_n)
            expected = "{} of {}".format(rank_str, suit_str)
            assert_equal(str(card), expected)


def test_card_queen_of_hearts_repr_str():
    card = Card(11, 3)
    assert_equal(repr(card), "Card(11, 3)")
    assert_equal(str(card), "Queen of Hearts")


def test_game_state_move_one_card_tableau_to_tableau():
    # move column 1 Jack of Hearts onto column 4 Queen of Clubs
    state2 = example_state_1.move_tableau_to_tableau(1, 0, 4)

    # there was a Queen of Hearts in the first column we can see now
    assert_list_equal(state2.tableau[1][0], [])
    assert_list_equal(state2.tableau[1][1], [Card(11, 3)])

    # Now the Jack of Hearts is in column 4
    assert_list_equal(state2.tableau[4][1], [Card(11, 2), Card(10, 3)])


def test_move_tableau_to_tableau():
    # move column 1 Jack of Hearts onto column 4 Queen of Clubs
    move = MoveTableauToTableau(1, 0, 4)
    state2 = example_state_1.apply_move(move)

    # there was a Queen of Hearts in the first column we can see now
    assert_list_equal(state2.tableau[1][0], [])
    assert_list_equal(state2.tableau[1][1], [Card(11, 3)])

    # Now the Jack of Hearts is in column 4
    assert_list_equal(state2.tableau[4][1], [Card(11, 2), Card(10, 3)])   


def test_game_state_move_two_tableau_to_tableau():
    # move column 1 Jack of Hearts onto column 4 Queen of Clubs
    state2 = example_state_1.move_tableau_to_tableau(1, 0, 4)

    # move those two cards onto column 0 King of Hearts
    state3 = state2.move_tableau_to_tableau(4, 0, 0)

    # There was a King of Diamonds in column 4 we can see now
    assert_list_equal(
        state3.tableau[4][0],
        [Card(2, 3), Card(1, 3), Card(0, 3)])
    
    assert_list_equal(state3.tableau[4][1], [Card(12, 2)])

    # Now there is a stack 3 deep visible in column 0
    assert_list_equal(
        state3.tableau[0][1],
        [Card(12, 3), Card(11, 2), Card(10, 3)])


def test_move_two_tableau_to_tableau():
    # move column 1 Jack of Hearts onto column 4 Queen of Clubs
    move1 = MoveTableauToTableau(1, 0, 4)
    state2 = example_state_1.apply_move(move1)

    # move those two cards onto column 0 King of Hearts
    move2 = MoveTableauToTableau(4, 0, 0)
    state3 = state2.apply_move(move2)

    # There was a King of Diamonds in column 4 we can see now
    assert_list_equal(
        state3.tableau[4][0],
        [Card(2, 3), Card(1, 3), Card(0, 3)])
    
    assert_list_equal(state3.tableau[4][1], [Card(12, 2)])

    # Now there is a stack 3 deep visible in column 0
    assert_list_equal(
        state3.tableau[0][1],
        [Card(12, 3), Card(11, 2), Card(10, 3)])


def test_game_state_move_tableau_to_tableau_wrong_card_raises_error():
    # King of hearts doesn't fit on Jack of hearts
    with assert_raises(InvalidMove):
        example_state_1.move_tableau_to_tableau(0, 0, 1)


def test_move_tableau_to_tableau_wrong_cards_raises_error():
    # King of hearts doesn't fit on Jack of hearts
    bad_move = MoveTableauToTableau(0, 0, 1)
    with assert_raises(InvalidMove):
        example_state_1.apply_move(bad_move)


def test_game_state_move_tableau_to_tableau_from_empty_raises_error():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3)

    # Now we have King-queen-jack in column 0, nothing in column 1
    with assert_raises(InvalidMove):
        state.move_tableau_to_tableau(1, 0, 0)


def test_move_tableau_to_tableau_from_empty_raises_error():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3)

    # Now we have King-queen-jack in column 0, nothing in column 1
    with assert_raises(InvalidMove):
        move = MoveTableauToTableau(1, 0, 0)
        state.apply_move(move)


def test_game_state_move_tableau_to_tableau_to_empty_raises_error():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3)

    # Now we have 8 of Hearts in column 2, nothing in column 1
    with assert_raises(InvalidMove):
        state.move_tableau_to_tableau(2, 0, 1)


def test_move_tableau_to_tableau_to_empty_raises_error():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3)

    # Now we have 8 of Hearts in column 2, nothing in column 1
    with assert_raises(InvalidMove):
        move = MoveTableauToTableau(2, 0, 1)
        state.apply_move(move)


def test_game_state_move_tableau_to_tableau_can_move_king_to_empty():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3)

    # Now we have King-queen-jack in column 0, nothing in column 1
    state = state.move_tableau_to_tableau(0, 0, 1)

    assert_list_equal(state.tableau[0], [[], []])
    assert_list_equal(
        state.tableau[1],
        [[], [Card(12, 3), Card(11, 2), Card(10, 3)]])


def test_game_state_move_tableau_to_tableau_can_move_king_to_empty():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3)

    # Now we have King-queen-jack in column 0, nothing in column 1
    move4 = MoveTableauToTableau(0, 0, 1)
    state = state.apply_move(move4)

    assert_list_equal(state.tableau[0], [[], []])
    assert_list_equal(
        state.tableau[1],
        [[], [Card(12, 3), Card(11, 2), Card(10, 3)]])


def test_game_state_move_tableau_to_foundation():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    move4 = MoveTableauToTableau(4, 0, 1)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3).apply_move(move4)

    # Now we have Ace of Hearts at the top of column 4
    state = state.move_tableau_to_foundation(4)
    assert_list_equal(state.tableau[4], [[Card(2, 3)], [Card(1, 3)]])
    assert_list_equal(state.foundation, [0, 0, 0, 1])


def test_move_tableau_to_foundation():
    move1 = MoveTableauToTableau(1, 0, 4)
    move2 = MoveTableauToTableau(4, 0, 0)
    move3 = MoveTableauToTableau(1, 0, 4)
    move4 = MoveTableauToTableau(4, 0, 1)
    state = example_state_1.apply_move(move1).apply_move(move2)
    state = state.apply_move(move3).apply_move(move4)

    # Now we have Ace of Hearts at the top of column 4
    move = MoveTableauToFoundation(4)
    state = state.apply_move(move)
    assert_list_equal(state.tableau[4], [[Card(2, 3)], [Card(1, 3)]])
    assert_list_equal(state.foundation, [0, 0, 0, 1])


def test_game_state_cant_move_tableau_to_foundation_too_high():
    for rank in range(1, 13):
        state = deepcopy(example_state_1)
        # switch the accessible card in column zero with a spade in the stock
        state.tableau[0][1][0] = state.stock[rank]
        state.stock[rank] = Card(12, 3)

        print(state)

        with assert_raises(InvalidMove):
            state.move_tableau_to_foundation(0)


def test_cant_move_tableau_to_foundation_too_high():
    for rank in range(1, 13):
        state = deepcopy(example_state_1)
        # switch the accessible card in column zero with a spade in the stock
        state.tableau[0][1][0] = state.stock[rank]
        state.stock[rank] = Card(12, 3)

        move = MoveTableauToFoundation(0)

        with assert_raises(InvalidMove):
            state.apply_move(move)


def test_game_state_turn_stock():
    state = example_state_1.turn_stock()
    assert_list_equal(
        state.stock,
        [Card(0, 0), Card(1, 0), Card(2, 0), Card(3, 0), Card(4, 0),
         Card(5, 0), Card(6, 0), Card(7, 0), Card(8, 0), Card(9, 0),
         Card(10, 0), Card(11, 0), Card(12, 0), Card(0, 1), Card(1, 1),
         Card(2, 1), Card(3, 1), Card(4, 1), Card(5, 1), Card(6, 1),
         Card(7, 1)])
    assert_list_equal(state.waste, [Card(10, 1), Card(9, 1), Card(8, 1)])


def test_turn_stock():
    state = example_state_1.apply_move(TurnStock())
    assert_list_equal(
        state.stock,
        [Card(0, 0), Card(1, 0), Card(2, 0), Card(3, 0), Card(4, 0),
         Card(5, 0), Card(6, 0), Card(7, 0), Card(8, 0), Card(9, 0),
         Card(10, 0), Card(11, 0), Card(12, 0), Card(0, 1), Card(1, 1),
         Card(2, 1), Card(3, 1), Card(4, 1), Card(5, 1), Card(6, 1),
         Card(7, 1)])
    assert_list_equal(state.waste, [Card(10, 1), Card(9, 1), Card(8, 1)])

# make sure this works when the stock is empty and the waste has 1, 2, or more cards


def test_game_state_move_waste_to_tableau():
    raise NotImplementedError


def test_move_waste_to_tableau():
    raise NotImplementedError

def test_game_state_move_waste_to_tableau_nothing_there_raises_error():
    raise NotImplementedError


def test_move_waste_to_tableau_nothing_there_raises_error():
    raise NotImplementedError


def test_game_state_move_waste_to_tableau_bad_card_raises_error():
    raise NotImplementedError


def test_move_waste_to_tableau_bad_card_raises_error():
    raise NotImplementedError


def test_game_state_move_waste_to_tableau_empty_column_raises_error():
    raise NotImplementedError


def test_move_waste_to_tableau_empty_column_raises_error():
    raise NotImplementedError


def test_game_state_move_waste_to_tableau_king_to_empty_col():
    raise NotImplementedError


def test_move_waste_to_tableau_king_to_empty_col():
    raise NotImplementedError


# move foundation to tableau

# move waste to foundation

# valid moves

