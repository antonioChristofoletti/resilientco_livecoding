from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.user import User


class Event:
    type: str = 'event'

    def __init__(self, actor: User, target: User):
        self.actor: User = actor
        self.target: User = target

    def __str__(self) -> str:
        return f'{self.actor.username} -> {self.target.username}'


class Payment(Event):
    type: str = 'payment'

    def __init__(self, amount: float, actor: User, target: User, note: str | None):
        super().__init__(actor, target)
        self.id: str = str(uuid.uuid4())
        self.amount: float = float(amount)
        self.note: str | None = note

    def __str__(self) -> str:
        note_text = f' for {self.note}' if self.note else ''
        return f'{self.actor.username} paid {self.target.username} ${self.amount:.2f}{note_text}'


class FriendshipEvent(Event):
    type: str = 'friend'

    def __str__(self) -> str:
        return f'{self.actor.username} added {self.target.username} as a friend.'
