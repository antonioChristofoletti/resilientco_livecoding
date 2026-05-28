from __future__ import annotations

from src.models.events import Event, FriendshipEvent, Payment
from src.models.user import User

# This class is a model and service at the same time. Keeping it in model for simplicity, 
# but in a real application, we would likely want to separate these concerns.
class MiniVenmo:
    def create_user(self, username: str, balance: float, credit_card_number: str) -> User:
        user = User(username)
        user.add_to_balance(balance)
        user.add_credit_card(credit_card_number)
        return user

    def render_feed(self, feed: list[Event]) -> None:
        for item in feed:
            print(str(item))