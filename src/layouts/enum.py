from typing import Dict, Set


class Enum:
    """Mapping of str values to uint32 integer."""

    _MAX_VAL = 4294967295  # 2^32 - 1

    def __init__(self, values: Dict[str, int]):
        self._values: Dict[str, int] = {}
        seen: Set[int] = set()
        for key, val in values.items():
            if val in seen:
                raise ValueError("duplicate enum value", val)
            if val > self._MAX_VAL:
                raise ValueError("invalid enum value", val)
            self._values[key] = val
            seen.add(val)

    def __validate_key(self, key: str):
        if key not in self._values:
            raise ValueError("invalid enum key", key)

    def __find_key(self, value: int) -> str:
        enum_tuple = next(((k, v) for k, v in self._values.items() if v == value), None)
        if not enum_tuple:
            raise ValueError("invalid enum value", value)
        return enum_tuple[0]

    def key(self, value: int) -> str:
        return self.__find_key(value)

    def value(self, key: str) -> int:
        self.__validate_key(key)
        return self._values[key]

    def encode(self, key: str) -> bytes:
        self.__validate_key(key)
        return self._values[key].to_bytes(4, byteorder="little")

    def decode(self, encoded_enum: bytes) -> str:
        value = int.from_bytes(encoded_enum, byteorder="little")
        return self.__find_key(value)
