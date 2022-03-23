import re
from abc import ABC, abstractmethod
from typing import Any

INT_REGEX = r'(^|\-)[0-9]+$'


class AbstractValidator(ABC):
    @abstractmethod
    def is_valid(self, value: Any) -> bool:
        pass


class IntValidator(AbstractValidator):
    def __init__(self, min_val: int, max_val: int, global_min=None):
        """:param min_val: minimal value of valid integer (inclusively).
        :param max_val: maximal value of valid integer (inclusively)."""
        super().__init__()
        self.min_val, self.max_val = min_val, max_val
        self.global_min = global_min if global_min is not None else min_val

    def is_valid(self, value: str) -> bool:
        """:param value: value to validate.
        :return: True if value is a valid integer (validates by regular expression)
        and belongs to interval [min_val, max_val]."""
        return bool(re.match(INT_REGEX, value)) and self.min_val <= int(value) <= self.max_val

    def update_bounds(self, min_val=None, max_val=None):
        if min_val is not None:
            self.min_val = min_val
            if min_val > self.max_val:
                self.max_val = min_val
        if max_val is not None:
            self.max_val = max(max_val, self.global_min)
            if self.max_val < self.min_val:
                self.min_val = self.max_val
