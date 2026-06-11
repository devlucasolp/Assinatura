"""
Objetos de valor do domínio — encapsulam primitivos conforme Object Calisthenics R3/R4.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MessageText:
    value: str

    def lower(self) -> "MessageText":
        return MessageText(self.value.lower())

    def __contains__(self, substring: str) -> bool:
        return substring in self.value

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Intent:
    value: str

    def __str__(self) -> str:
        return self.value


def _br_variants(phone: str) -> frozenset[str]:
    """Retorna o número e sua variante brasileira (12 ↔ 13 dígitos) para lidar com o 9 extra."""
    if not phone.startswith("55") or len(phone) not in (12, 13):
        return frozenset({phone})
    ddd, number = phone[2:4], phone[4:]
    if len(phone) == 12:
        return frozenset({phone, f"55{ddd}9{number}"})
    if number.startswith("9"):
        return frozenset({phone, f"55{ddd}{number[1:]}"})
    return frozenset({phone})


class AuthorizedPhones:
    """Coleção de primeira classe (R4) para os números autorizados da Gabi."""

    def __init__(self, *raw_phones: str) -> None:
        self._phones: frozenset[str] = frozenset(p for p in raw_phones if p)

    def allows(self, phone: PhoneNumber) -> bool:
        return bool(_br_variants(phone.value) & self._phones)

    def denies(self, phone: PhoneNumber) -> bool:
        return not self.allows(phone)
