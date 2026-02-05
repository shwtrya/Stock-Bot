"""Filter parsing utilities."""

from dataclasses import dataclass
from typing import List
import re


@dataclass(frozen=True)
class FilterCondition:
    field: str
    operator: str
    value: str


_FILTER_PATTERN = re.compile(
    r"^(?P<field>[a-zA-Z0-9_]+)\s*(?P<op><=|>=|==|=|<|>)\s*(?P<value>.+)$"
)


def parse_filter_expression(expression: str) -> FilterCondition:
    match = _FILTER_PATTERN.match(expression.strip())
    if not match:
        raise ValueError(f"Invalid filter expression: {expression}")
    return FilterCondition(
        field=match.group("field"),
        operator=match.group("op"),
        value=match.group("value").strip(),
    )


def parse_filters(text: str) -> List[FilterCondition]:
    if not text.strip():
        return []
    expressions = [chunk.strip() for chunk in text.split("+") if chunk.strip()]
    return [parse_filter_expression(expr) for expr in expressions]
