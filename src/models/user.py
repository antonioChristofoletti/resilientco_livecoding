from __future__ import annotations

import re

from src.models.events import Event, FriendshipEvent, Payment
from src.models.exceptions import CreditCardException, PaymentException, UsernameException


class User:

    def __init__(self, username: str):
        self.credit_card_number: str | None = None
        self.balance: float = 0.0
        self.activity: list[Event] = []
        self.friends: set[User] = set()

        if self._is_valid_username(username):
            self.username: str = username
        else:
            raise UsernameException('Username not valid.')

    def retrieve_feed(self) -> list[Event]:
        return list(self.activity)

    def add_friend(self, new_friend: User) -> FriendshipEvent | None:
        if self.username == new_friend.username:
            raise PaymentException('User cannot add themselves as a friend.')

        # Maybe we should raise an exception here instead of silently ignoring? For simplicity, just returning None for now.
        if new_friend in self.friends:
            return None

        self.friends.add(new_friend)
        new_friend.friends.add(self)

        friend_event = FriendshipEvent(self, new_friend)
        self.activity.append(friend_event)
        new_friend.activity.append(friend_event)

        return friend_event

    def add_to_balance(self, amount: float) -> None:
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number: str) -> None:
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number
        else:
            raise CreditCardException('Invalid credit card number.')

    # There are some overlapping checks in the pay methods, keeping the way It is for simplicity.
    def pay(self, target: User, amount: float, note: str) -> Payment:
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        if amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        if self.balance >= amount:
            return self.pay_with_balance(target, amount, note)

        return self.pay_with_card(target, amount, note)

    def pay_with_card(self, target: User, amount: float, note: str) -> Payment:
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')
        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')
        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        self.activity.append(payment)
        target.activity.append(payment)

        return payment

    def pay_with_balance(self, target: User, amount: float, note: str) -> Payment:
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')
        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')
        elif self.balance < amount:
            raise PaymentException('Insufficient balance to make the payment.')

        self.balance -= amount
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        self.activity.append(payment)
        target.activity.append(payment)

        return payment

    def _is_valid_credit_card(self, credit_card_number: str) -> bool:
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username: str) -> bool:
        return re.match(r'^[A-Za-z0-9_-]{4,15}$', username) is not None

    def _charge_credit_card(self, credit_card_number: str) -> None:
        pass
