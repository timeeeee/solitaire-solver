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


# state with column 1 of the tableau entirely empty
_s = GameState(DECK)
_s = _s.apply_move(MoveTableauToTableau(1, 0, 4))
_s = _s.apply_move(MoveTableauToTableau(4, 0, 0))
empty_col_1_state = _s.apply_move(MoveTableauToTableau(1, 0, 4))


def test_empty_col_example_state():
    assert_list_equal(empty_col_1_state.tableau[1], [[], []])


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


def test_turn_stock_empty_stock():
    s = example_state_1

    # start with 24 cards in stock, waste is empty
    assert_equal(len(s.stock), 24)
    assert_equal(len(s.waste), 0)

    for _ in range(8):
        s = s.apply_move(TurnStock())

    # now the stock is empty and there are 24 cards in the waste
    assert_equal(len(s.stock), 0)
    assert_equal(len(s.waste), 24)

    # next time the waste gets rotated back into the stock
    s = s.apply_move(TurnStock())
    assert_equal(len(s.stock), 21)
    assert_equal(len(s.waste), 3)


def test_turn_stock_two_cards_in_stock():
    s = example_state_1

    for _ in range(5):
        s = s.apply_move(TurnStock())

    # move a card onto the tableau
    s = s.apply_move(MoveWasteToTableau(1))

    for _ in range(3):
        s = s.apply_move(TurnStock())

    # stock is empty, 23 cards in waste
    assert_equal(len(s.stock), 0)
    assert_equal(len(s.waste), 23)

    # next time the waste gets rotated back into the stock
    s = s.apply_move(TurnStock())
    assert_equal(len(s.stock), 20)
    assert_equal(len(s.waste), 3)

    for _ in range(6):
        s = s.apply_move(TurnStock())

    # now there are two cards left in stock
    assert_equal(len(s.stock), 2)
    assert_equal(len(s.waste), 21)

    # this time, TurnStock only flips those two cards
    s = s.apply_move(TurnStock())

    assert_equal(len(s.stock), 0)
    assert_equal(len(s.waste), 23)


def test_turn_stock_one_card_in_stock():
    s = example_state_1

    for _ in range(5):
        s = s.apply_move(TurnStock())

    # move a card onto the tableau
    s = s.apply_move(MoveWasteToTableau(1))
    s = s.apply_move(MoveWasteToTableau(6))

    for _ in range(3):
        s = s.apply_move(TurnStock())

    # stock is empty, 22 cards in waste
    assert_equal(len(s.stock), 0)
    assert_equal(len(s.waste), 22)

    # next time the waste gets rotated back into the stock
    s = s.apply_move(TurnStock())
    assert_equal(len(s.stock), 19)
    assert_equal(len(s.waste), 3)

    for _ in range(6):
        s = s.apply_move(TurnStock())

    # now there is one card left in stock
    assert_equal(len(s.stock), 1)
    assert_equal(len(s.waste), 21)

    # this time, TurnStock only flips that card
    s = s.apply_move(TurnStock())

    assert_equal(len(s.stock), 0)
    assert_equal(len(s.waste), 22)


def test_game_state_move_waste_to_tableau():
    s = example_state_1

    for _ in range(5):
        s = s.apply_move(TurnStock())

    # move 10 of Spades to Jack of Hearts on tableau
    s = s.move_waste_to_tableau(1)

    assert_equal(len(s.waste), 14)
    assert_list_equal(s.tableau[1][1], [Card(10, 3), Card(9, 0)])


def test_move_waste_to_tableau():
    s = example_state_1

    for _ in range(5):
        s = s.apply_move(TurnStock())

    # move 10 of Spades to Jack of Hearts on tableau
    s = s.apply_move(MoveWasteToTableau(1))

    assert_equal(len(s.waste), 14)
    assert_list_equal(s.tableau[1][1], [Card(10, 3), Card(9, 0)])


def test_game_state_move_waste_to_tableau_nothing_there_raises_error():
    # at first the waste is empty
    assert_list_equal(example_state_1.waste, [])

    # so we can't take anything from it
    with assert_raises(InvalidMove):
        example_state_1.move_waste_to_tableau(0)


def test_move_waste_to_tableau_nothing_there_raises_error():
    # at first the waste is empty
    assert_list_equal(example_state_1.waste, [])

    # so we can't take anything from it
    with assert_raises(InvalidMove):
        example_state_1.apply_move(MoveWasteToTableau(0))


def test_game_state_move_waste_to_tableau_bad_card_raises_error():
    # try moving Jack of Diamonds onto each column...
    for col in range(7):
        # ... except 4 because it would fit under the Queen of Clubs
        if col == 4:
            continue

        with assert_raises(InvalidMove):
            example_state_1.move_waste_to_tableau(col)


def test_move_waste_to_tableau_bad_card_raises_error():
    # try moving Jack of Diamonds onto each column...
    for col in range(7):
        # ... except 4 because it would fit under the Queen of Clubs
        if col == 4:
            continue

        with assert_raises(InvalidMove):
            example_state_1.apply_move(MoveWasteToTableau(col))


def test_game_state_move_waste_to_tableau_empty_column_raises_error():
    # try to move card from waste to empty column
    with assert_raises(InvalidMove):
        empty_col_1_state.move_waste_to_tableau(1)


def test_move_waste_to_tableau_empty_column_raises_error():
    # try to move card from waste to empty column
    with assert_raises(InvalidMove):
        empty_col_1_state.apply_move(MoveWasteToTableau(1))


def test_game_state_move_waste_to_tableau_king_to_empty_col():
    state = empty_col_1_state
    for _ in range(4):
        state = state.apply_move(TurnStock())

    # Move King of Clubs into empty column 1
    state = state.move_waste_to_tableau(1)
    assert_equal(len(state.waste), 11)
    assert_list_equal(state.tableau[1], [[], [Card(12, 0)]])


def test_move_waste_to_tableau_king_to_empty_col():
    state = empty_col_1_state
    for _ in range(4):
        state = state.apply_move(TurnStock())

    # Move King of Clubs into empty column 1
    state = state.apply_move(MoveWasteToTableau(1))
    assert_equal(len(state.waste), 11)
    assert_list_equal(state.tableau[1], [[], [Card(12, 0)]])


def test_game_state_move_foundation_to_tableau():
    raise NotImplementedError


def test_move_foundation_to_tableau():
    raise NotImplementedError


def test_game_state_move_foundation_to_tableau_bad_suit():
    raise NotImplementedError


def test_move_foundation_to_tableau_bad_suit():
    raise NotImplementedError


def test_game_state_move_foundation_to_tableau_bad_rank():
    raise NotImplementedError


def test_move_foundation_to_tableau_bad_rank():
    raise NotImplementedError


def test_game_state_move_foundation_to_tableau_empty_column():
    # can't move a card to an empty column in the tableau...

    # ... unless it's a king!
    raise NotImplementedError


def test_move_foundation_to_tableau_empty_column():
    # can't move a card to an empty column in the tableau...

    # ... unless it's a king!
    raise NotImplementedError


def test_game_state_move_foundation_to_tableau_empty_foundation():
    with assert_raises(InvalidMove):
        example_state_1.move_foundation_to_tableau(0, 0)


def test_move_foundation_to_tableau_empty_foundation():
    with assert_raises(InvalidMove):
        move = MoveFoundationToTableau(0, 0)
        example_state_1.apply_move(move)


def test_game_state_move_waste_to_foundation():
    raise NotImplementedError


def test_move_waste_to_foundation():
    raise NotImplementedError


def test_game_state_move_waste_to_foundation_bad_card():
    raise NotImplementedError


def test_move_waste_to_foundation_bad_card():
    raise NotImplementedError


def test_turn_stock_equals_turn_stock():
    move1 = TurnStock()
    move2 = TurnStock()
    assert_equal(move1, move2)


def test_move_tableau_to_tableau_equal_to():
    for source_col in range(7):
        for source_row in range(12):
            for target_col in range(7):
                move1 = MoveTableauToTableau(
                    source_col, source_row, target_col)
                move2 = MoveTableauToTableau(
                    source_col, source_row, target_col)
                assert_equal(move1, move2)


def test_move_tableau_to_tableau_source_col_not_equal():
    assert_not_equal(
        MoveTableauToTableau(0, 0, 0), MoveTableauToTableau(1, 0, 0))


def test_move_tableau_to_tableau_source_row_not_equal():
    assert_not_equal(
        MoveTableauToTableau(0, 0, 0), MoveTableauToTableau(0, 1, 0))


def test_move_tableau_to_tableau_target_col_not_equal():
    assert_not_equal(
        MoveTableauToTableau(0, 0, 0), MoveTableauToTableau(0, 0, 1))


def test_move_tableau_to_foundation_equal():
    for col in range(7):
        move1 = MoveTableauToFoundation(col)
        move2 = MoveTableauToFoundation(col)
        assert_equal(move1, move2)


def test_move_tableau_to_foundation_source_col_not_equal():
    for col1 in range(7):
        move1 = MoveTableauToFoundation(col1)
        for col2 in range(7):
            move2 = MoveTableauToFoundation(col2)
            if col1 != col2:
                assert_not_equal(move1, move2)


def test_move_waste_to_tableau_equal():
    for col in range(7):
        move1 = MoveWasteToTableau(col)
        move2 = MoveWasteToTableau(col)
        assert_equal(move1, move2)


def test_move_waste_to_tableau_target_col_not_equal():
    for col1 in range(7):
        move1 = MoveWasteToTableau(col1)
        for col2 in range(7):
            if col1 != col2:
                move2 = MoveWasteToTableau(col2)
                assert_not_equal(move1, move2)


def test_move_waste_to_foundation_equal():
    move1 = MoveWasteToFoundation()
    move2 = MoveWasteToFoundation()
    assert_equal(move1, move2)


def test_move_waste_to_foundation_base_class_not_equal():
    assert_not_equal(MoveWasteToFoundation(), Move())


def test_move_foundation_to_tableau_equal():
    for source_col in range(4):
        for target_col in range(7):
            move1 = MoveFoundationToTableau(source_col, target_col)
            move2 = MoveFoundationToTableau(source_col, target_col)
            assert_equal(move1, move2)


def test_move_foundation_to_tableau_source_col_not_equal():
    for source_col1 in range(4):
        for source_col2 in range(4):
            if source_col1 == source_col2:
                continue

            for target_col in range(7):
                move1 = MoveFoundationToTableau(source_col1, target_col)
                move2 = MoveFoundationToTableau(source_col2, target_col)
                assert_not_equal(move1, move2)


def test_move_foundation_to_tableau_target_col_not_equal():
    for target_col1 in range(7):
        for target_col2 in range(7):
            if target_col1 == target_col2:
                continue

            for source_col in range(4):
                move1 = MoveFoundationToTableau(source_col, target_col1)
                move2 = MoveFoundationToTableau(source_col, target_col2)


def test_valid_moves_1():
    """
    Turn stock, move waste to tableau, move tableau to tableau
    """
    state = example_state_1
    for _ in range(5):
        state = state.turn_stock()

    valid_moves = set(state.valid_moves())
    expected = set([
        TurnStock(), MoveWasteToTableau(1), MoveTableauToTableau(1, 0, 4),
        MoveTableauToTableau(4, 0, 0)])
    assert_set_equal(valid_moves, expected)


def test_valid_moves_2():
    """
    turn stock, move waste king to tableau, move tableau king to tableau
    """
    state = empty_col_1_state
    for _ in range(4):
        state = state.turn_stock()

    valid_moves = set(state.valid_moves())
    expected = set([
        MoveWasteToTableau(1), TurnStock(), MoveTableauToTableau(0, 0, 1),
        MoveTableauToTableau(4, 0, 1)])
    assert_set_equal(valid_moves, expected)


def test_valid_moves_moves_to_foundation():
    state = example_state_1

    # get an ace at the top of the waste
    for _ in range(8):
        state = state.turn_stock()

    # make an ace accessible on col 6 of tableau
    state.tableau[6][0][4] = Card(11, 1)
    state.tableau[6][1][0] = Card(0, 2)

    valid_moves = set(state.valid_moves())
    expected = set([
        TurnStock(), MoveTableauToTableau(1, 0, 4),
        MoveTableauToTableau(4, 0, 0), MoveWasteToFoundation(),
        MoveTableauToFoundation(6)])
    assert_set_equal(valid_moves, expected)


def test_valid_moves_foundation_to_tableau():
    state = example_state_1
    for _ in range(8):
        state = state.turn_stock()

    # put ace of spades onto the foundation
    state.apply_move(MoveWasteToFoundation())

    # make 2 of hearts accessible in tableau col 3
    state.tableau[3][1][0] = Card(2, 3)
    state.tableau[4][0][0] = Card(3, 3)

    valid_moves = set(state.valid_moves())
    expected = set([
        TurnStock(), MoveTableauToTableau(1, 0, 4),
        MoveTableauToTableau(4, 0, 0), MoveWasteToFoundation(),
        MoveFoundationToTableau(0, 3)
    ])


def test_card_hash():
    raise NotImplementedError


def test_game_state_hash():
    raise NotImplementedError


def test_game_state_hash_tableau_column_order():
    raise NotImplementedError


def test_card_less_than_lt():
    for smaller_index, smaller in enumerate(DECK):
        for larger in DECK[smaller_index+1:]:
            assert(smaller < larger)


def test_card_equal_lt():
    for card in DECK:
        assert_false(card < card)


def test_card_greater_than_lt():
    for smaller_index, smaller in enumerate(DECK):
        for larger in DECK[smaller_index+1:]:
            assert_false(larger < smaller)
