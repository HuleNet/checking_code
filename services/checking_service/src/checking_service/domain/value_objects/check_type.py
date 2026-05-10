from checking_service.domain.value_objects import BaseEnum


class CheckType(BaseEnum):
    EXACT_MATCH = "EXACT_MATCH"
    IGNORE_WHITESPACE = "IGNORE_WHITESPACE"
    LINE_BY_LINE = "LINE_BY_LINE"
    FLOAT_COMPARE = "FLOAT_COMPARE"
