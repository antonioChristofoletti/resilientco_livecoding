import pytest

from src.models.events import Event, FriendshipEvent, Payment
from src.models.exceptions import CreditCardException, FriendshipException, PaymentException, UsernameException
from src.models.mini_venmo import MiniVenmo
from src.models.user import User


@pytest.fixture
def venmo() -> MiniVenmo:
    return MiniVenmo()


@pytest.fixture
def bobby_and_carol(venmo):
    bobby = venmo.create_user('Bobby', 5.00, '4111111111111111')
    carol = venmo.create_user('Carol', 10.00, '4242424242424242')
    return bobby, carol


class TestUserCreation:

    def test_create_user_sets_username_balance_and_card(self, venmo):
        user = venmo.create_user('Alice', 20.0, '4111111111111111')

        assert user.username == 'Alice'
        assert user.balance == 20.0
        assert user.credit_card_number == '4111111111111111'

    def test_create_user_with_invalid_username_raises(self):
        with pytest.raises(UsernameException):
            User('bad')


class TestCreditCard:

    def test_add_credit_card_only_once(self, venmo):
        user = venmo.create_user('Dave', 0.0, '4111111111111111')

        with pytest.raises(CreditCardException):
            user.add_credit_card('4242424242424242')

    def test_add_credit_card_invalid_number_raises(self):
        user = User('Eve123')

        with pytest.raises(CreditCardException):
            user.add_credit_card('1234567890')


class TestPayment:

    def test_pay_with_balance_reduces_source_balance_and_records_payment(self, bobby_and_carol):
        bobby, carol = bobby_and_carol
        payment = bobby.pay(carol, 5.00, 'Coffee')

        assert isinstance(payment, Payment)
        assert bobby.balance == 0.0
        assert carol.balance == 15.0
        assert payment in bobby.activity
        assert payment in carol.activity

    def test_pay_with_card_uses_credit_card_when_balance_is_insufficient(self, bobby_and_carol):
        bobby, carol = bobby_and_carol
        payment = carol.pay(bobby, 15.00, 'Lunch')

        assert isinstance(payment, Payment)
        assert payment.actor is carol
        assert payment.target is bobby
        assert carol.balance == 10.0
        assert bobby.balance == 20.0

    def test_pay_negative_amount_raises(self, bobby_and_carol):
        bobby, carol = bobby_and_carol

        with pytest.raises(PaymentException):
            bobby.pay(carol, -1.00, 'Bad amount')

    def test_pay_with_card_self_raises(self, venmo):
        user = venmo.create_user('Fred', 5.00, '4111111111111111')

        with pytest.raises(PaymentException):
            user.pay_with_card(user, 1.00, 'Self payment')

    def test_pay_with_balance_self_raises(self, venmo):
        user = venmo.create_user('Gina', 5.00, '4111111111111111')

        with pytest.raises(PaymentException):
            user.pay_with_balance(user, 1.00, 'Self payment')

    def test_pay_with_card_negative_amount_raises(self):
        payer = User('NoCard1')
        payer.add_credit_card('4111111111111111')
        receiver = User('Receiver1')

        with pytest.raises(PaymentException):
            payer.pay_with_card(receiver, -1.00, 'Bad amount')

    def test_pay_with_balance_negative_amount_raises(self):
        payer = User('Saver1')
        payer.add_to_balance(10.00)
        receiver = User('Receiver2')

        with pytest.raises(PaymentException):
            payer.pay_with_balance(receiver, -5.00, 'Bad amount')

    def test_pay_with_balance_insufficient_funds_raises(self):
        payer = User('Saver2')
        payer.add_to_balance(2.00)
        receiver = User('Receiver3')

        with pytest.raises(PaymentException):
            payer.pay_with_balance(receiver, 5.00, 'Too much')

    def test_pay_self_raises(self):
        user = User('Hank123')
        user.add_to_balance(5.00)

        with pytest.raises(PaymentException, match='User cannot pay themselves.'):
            user.pay(user, 5.00, 'Self payment')

    def test_pay_with_card_requires_credit_card(self):
        payer = User('NoCard1')
        receiver = User('Receiver1')

        with pytest.raises(PaymentException, match='Must have a credit card to make a payment.'):
            payer.pay_with_card(receiver, 5.00, 'No card')


class TestFriendship:

    def test_add_friend_is_mutual_and_records_friendship_event(self, bobby_and_carol):
        bobby, carol = bobby_and_carol
        event = bobby.add_friend(carol)

        assert isinstance(event, FriendshipEvent)
        assert event.actor is bobby
        assert event.target is carol
        assert carol in bobby.friends
        assert bobby in carol.friends
        assert event in bobby.activity
        assert event in carol.activity

    def test_add_friend_returns_none_when_already_friends(self, bobby_and_carol):
        bobby, carol = bobby_and_carol
        bobby.add_friend(carol)
        second_event = bobby.add_friend(carol)

        assert second_event is None
        assert sum(1 for item in bobby.activity if isinstance(item, FriendshipEvent)) == 1

    def test_add_self_friend_raises(self, bobby_and_carol):
        bobby, _ = bobby_and_carol

        with pytest.raises(FriendshipException):
            bobby.add_friend(bobby)


class TestFeed:

    def test_retrieve_feed_returns_a_copy_of_activity(self, bobby_and_carol):
        bobby, _ = bobby_and_carol
        feed = bobby.retrieve_feed()
        feed.append('mutated')

        assert 'mutated' not in bobby.activity

    def test_render_feed_prints_events(self, capsys, bobby_and_carol):
        bobby, carol = bobby_and_carol
        bobby.pay(carol, 5.00, 'Coffee')
        carol.pay(bobby, 15.00, 'Lunch')
        bobby.add_friend(carol)

        venmo = MiniVenmo()
        venmo.render_feed(bobby.retrieve_feed())

        captured = capsys.readouterr()
        assert 'Bobby paid Carol $5.00 for Coffee' in captured.out
        assert 'Carol paid Bobby $15.00 for Lunch' in captured.out
        assert 'Bobby added Carol as a friend.' in captured.out


class TestEvents:

    def test_event_str_returns_actor_to_target(self, bobby_and_carol):
        bobby, carol = bobby_and_carol
        event = Event(bobby, carol)

        assert str(event) == 'Bobby -> Carol'
