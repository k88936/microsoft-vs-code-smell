# this code is aigc
from abc import ABC, abstractmethod
from typing import Generic, TypeVar


EventT = TypeVar("EventT")


class Observer(ABC, Generic[EventT]):

    @abstractmethod
    def on_notify(self, event: EventT) -> None:
        """React to one event published by a subject."""


class Subject(Generic[EventT]):
    def __init__(self) -> None:
        self._observers: list[Observer[EventT]] = []

    def add_observer(self, observer: Observer[EventT]) -> None:
        """Subscribe ``observer`` if it is not already subscribed."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer[EventT]) -> None:
        """Unsubscribe ``observer``; do nothing if it was not subscribed."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: EventT) -> None:
        """Deliver ``event`` once to every currently subscribed observer."""
        for observer in tuple(self._observers):
            observer.on_notify(event)
