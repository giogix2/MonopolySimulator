import pytest
from monosim.player import Player
from monosim.board import get_roads, get_board, get_properties, get_community_chest_cards, get_bank
import random


def test_roll_dice():
    """ Test function roll_dice. Check if the values returns are lower than 1 or higher than 6. Run
        the function several times with different random seeds to change the output of the returned values.
    """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    for seed in range(1000, 5000):
        random.seed(seed)
        value1, value2 = player1.roll_dice()
        assert 0 < value1 <= 6
        assert 0 < value2 <= 6


def test_get_state():
    """ Test function get_state. """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    dict_state = player1.get_state()

    assert dict_state['name'] == 'player1'
    assert dict_state['number'] == 1
    assert dict_state['cash'] == 1440
    assert dict_state['owned_roads'] == ['old kent road']
    assert dict_state['owned_houses_hotels'] == {'old kent road': (0, 0)}


def test_pay_opponent():
    """ Test function pay_opponent when player has enough money"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player2 = Player('player2', 2, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player1.meet_other_players([player2]), player2.meet_other_players([player1])
    player1.pay_opponent(player2._name, 10)
    assert player1._cash == 1490
    assert player2._cash == 1510


def test_pay_opponent_no_money():
    """ Test function pay_opponent when player doesn't have enough money. The function throws
    an assert error. """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player2 = Player('player2', 2, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player1.meet_other_players([player2]), player2.meet_other_players([player1])
    player1.set_cash(20)

    with pytest.raises(AssertionError):
        player1.pay_opponent(player2._name, 30)


def test_mortgage_roads():
    """ Test function mortgage when a road is bought. Test if property is set to 'is_mortgaged' and if
        money are moved from the total mortgageable amount to cash."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    road_name = 'old kent road'  # mortgage value 30
    dict_road_info = dict_roads[road_name]
    player1.buy(dict_road_info, road_name)
    assert player1._properties_total_mortgageable_amount == 30
    assert player1._properties_total_mortgageable_amount + player1._cash == 1470

    player1.set_cash(0)
    player1.mortgage(road_name, 'road')

    assert road_name in player1._list_mortgaged_roads
    assert player1._properties_total_mortgageable_amount == 0
    assert dict_roads[road_name]['is_mortgaged'] is True
    assert player1._cash == 30


def test_mortgage_properties():
    """ Test function mortgage when a station or utility is bought. Test if property is set to 'is_mortgaged' and if
        money are moved from the total mortgageable amount to cash."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    property_name = 'kings cross station'  # mortgage value 100
    dict_property_info = dict_properties[property_name]
    player1.buy_property(dict_property_info)
    assert player1._properties_total_mortgageable_amount == 100
    assert player1._properties_total_mortgageable_amount + player1._cash == 1400

    player1.set_cash(0)
    player1.mortgage(property_name, 'station')

    assert property_name in player1._list_mortgaged_stations
    assert player1._properties_total_mortgageable_amount == 0
    assert dict_properties[property_name]['is_mortgaged'] is True
    assert player1._cash == 100

    player1.set_cash(150)
    property_name = 'Electric company'  # mortgage value 75
    dict_property_info = dict_properties[property_name]
    player1.buy_property(dict_property_info)
    assert player1._properties_total_mortgageable_amount == 75
    assert player1._properties_total_mortgageable_amount + player1._cash == 75

    player1.mortgage(property_name, 'utility')

    assert property_name in player1._list_mortgaged_utilities
    assert player1._properties_total_mortgageable_amount == 0
    assert dict_properties[property_name]['is_mortgaged'] is True
    assert player1._cash == 75


def test_unmortgage_roads():
    """ Test function unmortgage when a road is bought and unmortgaged."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    road_name = 'old kent road'  # mortgage value 30, unmortgage value 33
    dict_road_info = dict_roads[road_name]
    player1.buy(dict_road_info, road_name)
    assert player1._properties_total_mortgageable_amount == 30
    assert player1._properties_total_mortgageable_amount + player1._cash == 1470
    player1.mortgage('old kent road', 'road')
    assert player1._properties_total_mortgageable_amount == 0
    assert player1.cash == 1470

    player1.unmortgage('old kent road', 'road')
    assert player1._properties_total_mortgageable_amount == 30
    assert player1._list_mortgaged_roads == []
    assert player1.cash == 1437


def test_unmortgage_properties():
    """ Test function unmortgage when a station or utility is bought and unmortgaged."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    property_name = 'kings cross station'  # mortgage value 100, unmortgage value 110
    dict_property_info = dict_properties[property_name]
    player1.buy_property(dict_property_info)

    property_name = 'Electric company'  # mortgage value 75, unmortgage value 83
    dict_property_info = dict_properties[property_name]
    player1.buy_property(dict_property_info)

    assert player1.cash == 1150
    assert player1._properties_total_mortgageable_amount == 175

    player1.mortgage('kings cross station', 'station')
    player1.mortgage('Electric company', 'utility')
    assert player1._properties_total_mortgageable_amount == 0
    assert player1.cash == 1325
    player1.unmortgage('kings cross station', 'station')
    player1.unmortgage('Electric company', 'utility')
    assert player1._properties_total_mortgageable_amount == 175
    assert player1.cash == 1132
    assert player1._list_mortgaged_stations == []
    assert player1._list_mortgaged_utilities == []


def test_mortgage_exceptions():
    """ Test function mortgage when exceptions are raised. Test exceptions raised when the wrong property type is
        passed and when the player doesn't own a given station."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    property_name = 'kings cross station'
    dict_property_info = dict_properties[property_name]
    player1.buy_property(dict_property_info)

    player1.set_cash(0)
    with pytest.raises(Exception):
        player1.mortgage(property_name, 'aaa')

    with pytest.raises(Exception):
        # Player 1 doesn't own the following station
        player1.mortgage('Fenchurch st. station', 'station')

    with pytest.raises(Exception):
        # Player 1 doesn't own the following road
        player1.mortgage('the angel islington', 'road')

    with pytest.raises(Exception):
        # Player 1 doesn't own the following road
        player1.mortgage('Electric company', 'utility')


def test_choose_mortgage_properties_only_roads():
    """ Test function choose_mortgage_properties when player has enough roads"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # buy three roads
    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')
    player1.buy(dict_roads['the angel islington'], 'the angel islington')

    assert player1.cash == 1280
    assert player1._properties_total_mortgageable_amount == 110

    list_expected_properties = [('road', 'old kent road')]
    list_result_properties = player1.choose_mortgage_properties(2)
    assert list_expected_properties == list_result_properties

    list_expected_properties = [('road', 'old kent road'),('road', 'whitechapel road')]
    list_result_properties = player1.choose_mortgage_properties(60)
    assert list_expected_properties == list_result_properties

    list_expected_properties = [('road', 'old kent road'),
                                ('road', 'whitechapel road'),
                                ('road', 'the angel islington')]
    list_result_properties = player1.choose_mortgage_properties(61)
    assert list_expected_properties == list_result_properties


def test_choose_mortgage_properties():
    """ Test function choose_mortgage_properties when player has 1 station or 1 station + 1 utility"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # buy station
    player1.buy_property(dict_properties['kings cross station'])
    assert player1.cash == 1300
    assert player1._properties_total_mortgageable_amount == 100

    list_expected_properties = [('station', 'kings cross station')]
    list_result_properties = player1.choose_mortgage_properties(99)
    assert list_expected_properties == list_result_properties

    # buy utility
    player1.buy_property(dict_properties['Electric company'])
    assert player1.cash == 1150
    assert player1._properties_total_mortgageable_amount == 175

    list_expected_properties = [('station', 'kings cross station'), ('utility', 'Electric company')]
    list_result_properties = player1.choose_mortgage_properties(174)
    assert list_expected_properties == list_result_properties


def test_choose_unmortgage_properties():
    """ Test function choose_unmortgage_properties"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy_property(dict_properties['kings cross station'])
    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['pentonville road'], 'pentonville road')
    assert player1._properties_total_mortgageable_amount == 190

    player1.mortgage('kings cross station', 'station')
    player1.mortgage('old kent road', 'road')
    player1.mortgage('pentonville road', 'road')

    player1.set_cash(10)  # hardcode cash
    list_unmortgage_properties = player1.choose_unmortgage_properties()
    assert list_unmortgage_properties == []

    player1.set_cash(34)
    list_unmortgage_properties = player1.choose_unmortgage_properties()
    assert list_unmortgage_properties == [('road', 'old kent road')]

    player1.set_cash(100)
    list_unmortgage_properties = player1.choose_unmortgage_properties()
    assert list_unmortgage_properties == [('road', 'old kent road'), ('road', 'pentonville road')]

    player1.set_cash(210)
    list_unmortgage_properties = player1.choose_unmortgage_properties()
    assert list_unmortgage_properties == [('road', 'old kent road'), ('road', 'pentonville road'), ('station', 'kings cross station')]


def test_choose_mortgage_properties_exceptions():
    """ Test function choose_mortgage_properties when Exceptions are thrown"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    with pytest.raises(Exception):
        # Player owns 0 properties. This function throws an exception (no properties owned)
        player1.choose_mortgage_properties(2)

    # buy station
    player1.buy_property(dict_properties['kings cross station'])
    assert player1.cash == 1300
    assert player1._properties_total_mortgageable_amount == 100

    with pytest.raises(Exception):
        # Player can only mortgage 100$. This function throws an exception (insufficient funds)
        player1.choose_mortgage_properties(101)


def test_get_money_from_mortgages_roads():
    """ Test get_money_from_mortgages function. Test cases when the player has enough money and doesn't need to
        mortgage and when player needs to mortgage all the owned roads"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # buy two properties
    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['pentonville road'], 'pentonville road')

    # Check player's cash and mortgageable amount
    player1.set_cash(60)
    assert player1._properties_total_mortgageable_amount == 90
    assert player1._cash == 60

    # player needs 40$ to buy Euston road
    road_price = dict_roads['euston road']['price']  # 100$
    amount_required = road_price - player1._cash  # 40$
    assert player1.have_enough_money(road_price) is False
    player1.get_money_from_mortgages(amount_required)
    assert player1._properties_total_mortgageable_amount == 0
    assert player1._cash == 150

    player1.buy(dict_roads['euston road'], 'euston road')
    assert player1._cash == 50

    # player wants to buy pall mall road (140$) but only has 50$. Function raises exception
    road_price = dict_roads['pall mall']['price']  # 140$
    amount_required = road_price - player1._cash  # 90$
    with pytest.raises(Exception):
        player1.get_money_from_mortgages(amount_required)


def test_get_money_from_mortgages_properties():
    """ Test get_money_from_mortgages function. Test cases when the player owns properties (stations, utilities)
        and needs to mortgage few of them."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # buy two properties
    player1.buy_property(dict_properties['kings cross station'])
    player1.buy_property(dict_properties['Electric company'])

    # Check player's cash and mortgageable amount
    player1.set_cash(60)
    assert player1._properties_total_mortgageable_amount == 175
    assert player1._cash == 60

    # player needs 140$ to buy Fenchurch st. station
    property_price = dict_properties['Fenchurch st. station']['price']
    amount_required = property_price - player1._cash
    assert player1.have_enough_money(property_price) is False
    player1.get_money_from_mortgages(amount_required)
    assert player1._properties_total_mortgageable_amount == 0
    assert player1._cash == 235
    assert player1._list_mortgaged_stations == ['kings cross station']
    assert player1._list_mortgaged_utilities == ['Electric company']


def test_mortgage_and_pay_rent_roads():
    """ Test function mortgage_and_pay_rent. Test cases when player has enough money to rent and when it needs
        to mortgage a road."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player2 = Player('player2', 2, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player1.meet_other_players([player2]), player2.meet_other_players([player1])

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player2.buy(dict_roads['pentonville road'], 'pentonville road')
    dict_property_info = dict_roads['pentonville road']
    player1.set_cash(10)

    # player1 has enough money. Function raises an exception.
    with pytest.raises(Exception):
        player1.mortgage_and_pay_rent(dict_property_info)

    # player1 doesn't enough money.
    player1.set_cash(4)
    assert dict_roads['old kent road']['is_mortgaged'] is False
    assert player1._properties_total_mortgageable_amount == 30
    player1.mortgage_and_pay_rent(dict_property_info)
    assert player1._cash == 26
    assert dict_roads['old kent road']['is_mortgaged'] is True
    assert player1._properties_total_mortgageable_amount == 0


def test_mortgage_and_pay_rent_properties():
    """ Test function mortgage_and_pay_rent. Test cases when player needs to mortgage a station."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player2 = Player('player2', 2, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player1.meet_other_players([player2]), player2.meet_other_players([player1])

    player1.buy_property(dict_properties['kings cross station'])
    player2.buy(dict_roads['pentonville road'], 'pentonville road')
    dict_property_info = dict_roads['pentonville road']

    # player1 enough money to pay the rent for pentonville road
    player1.set_cash(6)
    assert dict_properties['kings cross station']['is_mortgaged'] is False
    assert player1._properties_total_mortgageable_amount == 100
    player1.mortgage_and_pay_rent(dict_property_info)
    assert player1._cash == 98
    assert dict_properties['kings cross station']['is_mortgaged'] is True
    assert player1._properties_total_mortgageable_amount == 0


def test_mortgage_and_buy_roads():
    """ Test function mortgage_and_buy. Test use cases in which the player needs to mortgage a road."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.set_cash(31)
    assert dict_roads['old kent road']['is_mortgaged'] is False
    # buy property which cost 60
    player1.mortgage_and_buy(dict_roads['whitechapel road'], 'whitechapel road', 'road')
    assert player1._cash == 1
    assert player1._list_mortgaged_roads == ['old kent road']
    assert dict_roads['old kent road']['is_mortgaged'] is True
    assert player1._properties_total_mortgageable_amount == 30


def test_mortgage_and_buy_properties():
    """ Test function mortgage_and_buy. Test use cases in which the player wants to buy a station."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.set_cash(171)
    assert dict_roads['old kent road']['is_mortgaged'] is False
    # buy property which cost 60
    player1.mortgage_and_buy(dict_properties['kings cross station'], 'kings cross station', 'station')
    assert player1._cash == 1
    assert player1._list_mortgaged_roads == ['old kent road']
    assert dict_roads['old kent road']['is_mortgaged'] is True
    assert player1._properties_total_mortgageable_amount == 100

    with pytest.raises(Exception):
        #  Property type 'aaa' unrecognized. Raise an exception
        player1.mortgage_and_buy(dict_properties['Fenchurch st. station'], 'Fenchurch st. station', 'aaa')


def test_have_enough_money():
    """ Test function have_enough_money """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # buy three properties
    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')
    player1.buy(dict_roads['the angel islington'], 'the angel islington')

    assert player1.cash == 1280
    assert player1.have_enough_money(600, plus_mortgageable=False) is True
    assert player1.have_enough_money(1281, plus_mortgageable=False) is False

    # Total mortgageable is 110
    assert player1.have_enough_money(1281, plus_mortgageable=True) is True
    assert player1.have_enough_money(1391, plus_mortgageable=True) is False


def test_buy():
    """ Test buy function. Check if the bank receives money paid by the player. Check whether exceptions are
        raised. Make sure property are not bought when the player doesn't have enough money."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # Check player/bank money and property's ownership
    player1.buy(dict_roads['old kent road'], 'old kent road')
    assert player1.cash == 1440
    assert bank['cash'] == 5060
    assert dict_roads['old kent road']['belongs_to'] == 'player1'

    # Is exception raised when the player doesn't have enough money?
    player1.set_cash(0)
    with pytest.raises(Exception):
        player1.buy(dict_roads['whitechapel road'], 'whitechapel road')

    # Player shouldn't own last property due to lack of money
    assert player1._list_owned_roads == ['old kent road']


def test_buy_all_roads_of_same_color():
    """ Test buy function. Check if the color dictionary (_dict_owned_colors) is updated when all the roads of the
        same color are bought"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # Color brown
    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')
    assert player1.has_all_roads_of_color('brown') is True

    # Color light_blue
    player1.buy(dict_roads['the angel islington'], 'the angel islington')
    player1.buy(dict_roads['euston road'], 'euston road')
    assert player1.has_all_roads_of_color('light_blue') is False
    player1.buy(dict_roads['pentonville road'], 'pentonville road')
    assert player1.has_all_roads_of_color('light_blue') is True

    # Color purple
    player1.buy(dict_roads['pall mall'], 'pall mall')
    player1.buy(dict_roads['whitehall'], 'whitehall')
    assert player1.has_all_roads_of_color('purple') is False
    player1.buy(dict_roads['northumberland avenue'], 'northumberland avenue')
    assert player1.has_all_roads_of_color('purple') is True

    # Color orange
    player1.buy(dict_roads['bow street'], 'bow street')
    player1.buy(dict_roads['marlborough street'], 'marlborough street')
    assert player1.has_all_roads_of_color('orange') is False
    player1.buy(dict_roads['vine street'], 'vine street')
    assert player1.has_all_roads_of_color('orange') is True

    # Color red
    player1.set_cash(1500)
    player1.buy(dict_roads['strand'], 'strand')
    player1.buy(dict_roads['fleet street'], 'fleet street')
    assert player1.has_all_roads_of_color('red') is False
    player1.buy(dict_roads['trafalgar square'], 'trafalgar square')
    assert player1.has_all_roads_of_color('red') is True

    # Color yellow
    player1.buy(dict_roads['leicester square'], 'leicester square')
    player1.buy(dict_roads['coventry street'], 'coventry street')
    assert player1.has_all_roads_of_color('yellow') is False
    player1.buy(dict_roads['piccadilly'], 'piccadilly')
    assert player1.has_all_roads_of_color('yellow') is True

    # Color green
    player1.set_cash(1500)
    player1.buy(dict_roads['regent street'], 'regent street')
    player1.buy(dict_roads['oxford street'], 'oxford street')
    assert player1.has_all_roads_of_color('green') is False
    player1.buy(dict_roads['bond street'], 'bond street')
    assert player1.has_all_roads_of_color('green') is True

    # Color blue
    player1.set_cash(1500)
    player1.buy(dict_roads['park lane'], 'park lane')
    assert player1.has_all_roads_of_color('blue') is False
    player1.buy(dict_roads['mayfair'], 'mayfair')
    assert player1.has_all_roads_of_color('blue') is True


def test_buy_property():
    """ Test buy function. Check if the bank receives money paid by the player. Check whether exceptions are
        raised. Make sure property are not owned when player doesn't have enough money."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    # Check player/bank money and property's ownership
    player1.buy_property(dict_properties['kings cross station'])
    assert player1.cash == 1300
    assert bank['cash'] == 5200
    assert dict_properties['kings cross station']['belongs_to'] == 'player1'

    # Is exception raised when the player doesn't have enough money?
    player1.set_cash(0)
    with pytest.raises(Exception):
        player1.buy_property(dict_properties['Fenchurch st. station'])

    # Player shouldn't own last property due to lack of money
    assert player1._list_owned_stations == ['kings cross station']


def test_pay_bank():
    """ Test pay_bank function. """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    current_player_cash_amount = player1._cash
    current_bank_cash_amount = bank['cash']
    player1.pay_bank(200)
    assert player1._cash == current_player_cash_amount - 200
    assert bank['cash'] == current_bank_cash_amount + 200

    with pytest.raises(Exception):
        # Player has only 1300$. Exception should be raised.
        player1.pay_bank(1301)


def test_estimate_rent_road():
    """ Test estimate_rent_road function. Check if right amount is calculated when player owns all roads of one color.
    """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player2 = Player('player2', 2, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player1.meet_other_players([player2]), player2.meet_other_players([player1])

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')

    # Hardcoded assignment of property colors and houses/hotel
    player1._dict_owned_colors['brown'] = True
    player1._dict_owned_houses_hotels['old kent road'] = (0, 0)

    rent = player2.estimate_rent_road(dict_roads['old kent road'])
    assert rent == 4

    with pytest.raises(Exception):
        # Player 1 doesn't own euston road. Exception raised
        player2.estimate_rent_road(dict_roads['euston road'])


def test_estimate_rent_station():
    """ Test estimate_rent_station function.
        Check if right amount is calculated when player owns one or two stations. """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player2 = Player('player2', 2, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player1.meet_other_players([player2]), player2.meet_other_players([player1])

    player1.buy_property(dict_properties['kings cross station'])
    rent = player2.estimate_rent_station(dict_properties['kings cross station'])
    assert rent == 25

    with pytest.raises(Exception):
        # Player 1 doesn't own Fenchurch st. station. Exception raised
        player2.estimate_rent_station(dict_properties['Fenchurch st. station'])

    player1.buy_property(dict_properties['Fenchurch st. station'])
    rent = player2.estimate_rent_station(dict_properties['kings cross station'])
    assert rent == 50

    # Check if exception is raised when utility is passed instead of station.
    with pytest.raises(Exception):
        player2.estimate_rent_station(dict_properties['Electric company'])


def test_estimate_rent_utility():
    """ Test estimate_rent_utilities function.
        Check if right amount is calculated when player owns one or two utilities. """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player2 = Player('player2', 2, bank, list_board, dict_roads, dict_properties, community_cards_deck)
    player1.meet_other_players([player2]), player2.meet_other_players([player1])

    player1.buy_property(dict_properties['Electric company'])
    # Player 2 launches dice and gets 6
    player2._dice_value = 6

    rent = player2.estimate_rent_utility(dict_properties['Electric company'])
    assert rent == 24

    with pytest.raises(Exception):
        # Player 1 doesn't own Water works. Exception raised
        player2.estimate_rent_station(dict_properties['Water works'])

    player1.buy_property(dict_properties['water works'])
    # Player 2 launches dice and gets 10
    player2._dice_value = 10

    rent = player2.estimate_rent_utility(dict_properties['Electric company'])
    assert rent == 100

    # Check if exception is raised when station is passed instead of utility.
    with pytest.raises(Exception):
        player2.estimate_rent_station(dict_properties['Fenchurch st. station'])


def test_choose_house_hotel_to_buy():
    """ Test function choose_house_hotel_to_buy. Test case where player owns all the brown color roads. Test
        situations where the player: 1) already has all possible houses and hotels, 2) can buy a hotel 3) still
        needs to buy houses before buying hotels"""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')

    # Hardcoded assignment of houses and hotel
    player1._dict_owned_houses_hotels['old kent road'] = (4, 1)
    player1._dict_owned_houses_hotels['whitechapel road'] = (4, 1)
    res = player1.choose_house_hotel_to_buy()
    assert res == (None, None)

    player1._dict_owned_houses_hotels['old kent road'] = (4, 1)
    player1._dict_owned_houses_hotels['whitechapel road'] = (4, 0)
    res = player1.choose_house_hotel_to_buy()
    assert res == ('whitechapel road', 'hotel')

    player1._dict_owned_houses_hotels['old kent road'] = (4, 0)
    player1._dict_owned_houses_hotels['whitechapel road'] = (4, 0)
    res = player1.choose_house_hotel_to_buy()
    assert res[1] == 'hotel'

    player1._dict_owned_houses_hotels['old kent road'] = (4, 0)
    player1._dict_owned_houses_hotels['whitechapel road'] = (3, 0)
    res = player1.choose_house_hotel_to_buy()
    assert res == ('whitechapel road', 'house')


def test_buy_house():
    """ Test function buy_house(). """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')
    # Hardcoded assignment of houses and hotel
    player1._dict_owned_houses_hotels['old kent road'] = (2, 0)
    player1._dict_owned_houses_hotels['whitechapel road'] = (2, 0)

    player1.buy_house('old kent road')
    assert player1._dict_owned_houses_hotels['old kent road'] == (3, 0)
    player1.buy_house('old kent road')
    assert player1._dict_owned_houses_hotels['old kent road'] == (4, 0)

    with pytest.raises(Exception):
        # Player already has a maximum of 4 houses. Exception raised.
        player1.buy_house('old kent road')

    player1._cash = 10
    with pytest.raises(Exception):
        # The player has no enough money to buy a house. Exception raised.
        player1.buy_house('whitechapel road')

    player1._cash = 100
    bank['houses'] = 0 # Hardcoded number of houses owned by the bank
    with pytest.raises(Exception):
        # The bank has no more houses to sell. Exception raised.
        player1.buy_house('whitechapel road')


def test_buy_hotel():
    """ Test function buy_hotel(). """

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')

    # Hardcoded assignment of houses and hotel
    player1._dict_owned_houses_hotels['old kent road'] = (4, 0)
    player1.buy_hotel('old kent road')
    assert player1._dict_owned_houses_hotels['old kent road'] == (4, 1)

    with pytest.raises(Exception):
        # Player already has a maximum of 1 hotel. Exception raised.
        player1.buy_hotel('old kent road')

    player1._cash = 10
    with pytest.raises(Exception):
        # The player has no enough money to buy a hotel. Exception raised.
        player1.buy_hotel('whitechapel road')

    player1._cash = 100
    bank['hotels'] = 0  # Hardcoded number of houses owned by the bank
    with pytest.raises(Exception):
        # The bank has no more houses to sell. Exception raised.
        player1.buy_hotel('whitechapel road')


def test_choose_house_hotel_to_buy_player_doesnt_own_colors():
    """ Test function choose_house_hotel_to_buy. Test case where player doesn't own any color. The function returns
        None in this case."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    res = player1.choose_house_hotel_to_buy()
    assert res == (None, None)


def test_get_owned_colors():
    """ Test function get_owned_colors."""

    bank = get_bank()
    list_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, list_board, dict_roads, dict_properties, community_cards_deck)

    assert player1.get_owned_colors() == []  # initially the player doesn't own any color

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')
    assert player1.get_owned_colors() == ['brown']

    player1.buy(dict_roads['the angel islington'], 'the angel islington')
    player1.buy(dict_roads['euston road'], 'euston road')
    player1.buy(dict_roads['pentonville road'], 'pentonville road')

    assert player1.get_owned_colors() == ['brown', 'light_blue']


def test_community_chest_street_repair():
    """ Test function community_chest_street_repair. Test use cases when the player has enough money to pay and when
    does not have enough money, causing bankrupt.
    """

    bank = get_bank()
    dict_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, dict_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')
    player1.buy(dict_roads['whitechapel road'], 'whitechapel road')

    player1.buy(dict_roads['the angel islington'], 'the angel islington')
    player1.buy(dict_roads['euston road'], 'euston road')
    player1.buy(dict_roads['pentonville road'], 'pentonville road')

    player1.set_cash(900)  # hardcoded for testing purposes (in case we change the player's default cash in the future)
    player1.buy_house('old kent road')
    assert player1._cash == 850
    player1.community_chest_street_repair()
    assert player1._cash == 810

    player1.buy_house('old kent road')
    player1.buy_house('old kent road')
    player1.buy_house('old kent road')
    player1.buy_hotel('old kent road')

    # player bought 3 additional houses + 1 hotel for a total of 200
    # player pays 4 houses * 4 + 1 hotel * 115 = 275
    player1.community_chest_street_repair()
    assert player1._cash == 335

    # Test bankrupt
    player1.buy_house('whitechapel road')
    player1.buy_house('whitechapel road')
    player1.buy_house('whitechapel road')
    player1.buy_house('whitechapel road')
    player1.buy_hotel('whitechapel road')
    assert player1._cash == 85

    # Player needs 525 but only has 85
    player1.community_chest_street_repair()
    assert player1.has_lost() is True


def test_pay_tax():
    """ Test function pay_tax. Test use cases when the player has enough money to pay and when
        does not have enough money, causing bankrupt.
    """

    bank = get_bank()
    dict_board, dict_roads, dict_properties = get_board(), get_roads(), get_properties()
    dict_community_chest_cards = get_community_chest_cards()
    community_cards_deck = list(dict_community_chest_cards.keys())
    player1 = Player('player1', 1, bank, dict_board, dict_roads, dict_properties, community_cards_deck)

    player1.buy(dict_roads['old kent road'], 'old kent road')

    # Player pays
    player1.set_cash(900)  # hardcoded for testing purposes (in case we change the player's default cash in the future)
    player1.buy_house('old kent road')
    assert player1._cash == 850
    player1.pay_tax(40)
    assert player1._cash == 810

    # Player mortgages
    player1.set_cash(10)
    player1.pay_tax(20)
    assert player1._cash == 20

    # Player loses
    player1.pay_tax(50)
    assert player1.has_lost() is True
