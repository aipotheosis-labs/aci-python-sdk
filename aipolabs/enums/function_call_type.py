from enum import Enum


class AipolabsFunctionCallType(str, Enum):
    SEARCH = "search"
    FETCH = "fetch"
    EXECUTE = "execute"
    UNKNOWN = "unknown"
