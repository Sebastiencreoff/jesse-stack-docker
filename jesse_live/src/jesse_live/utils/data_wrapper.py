#! /usr/bin/env python
import inspect
from typing import Any, Dict


class DataWrapper:
    """Wraps dictionary to use as class attribute."""

    def __init__(self) -> None:
        pass

    def from_dict(self, data: Dict[str, any]):
        for key, value in data.items():
            setattr(self, key, self._convert(value))
        return self

    def _convert(self, data: Any):
        if isinstance(data, dict):
            return DataWrapper().from_dict(data)
        elif isinstance(data, list):
            return [self._convert(item) for item in data]
        else:
            return data

    def __contains__(self, prop: str) -> bool:
        """Check if object contains a key."""
        return prop in self.__dict__

    def __getattr__(self, prop: str) -> Any:
        if prop not in self.__dict__:
            raise AttributeError(f"Datawrapper doesn't have attribute {prop}")
        return getattr(self, prop)

    def items(self):
        for prop in self.__dict__:
            if prop.startswith("_") or inspect.isfunction(prop):
                continue
            yield prop, getattr(self, prop)

    def __repr__(self):
        return f"DataWrapper data: {self.to_dict()}"

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        def _to_dict(data):
            if isinstance(data, DataWrapper):
                return data.to_dict()
            elif isinstance(data, list):
                return [_to_dict(item) for item in data]
            else:
                return data

        return {key: _to_dict(value) for key, value in self.__dict__.items()}
