from enum import Enum


class AipolabsFunctionCallType(str, Enum):
    META_SEARCH = "meta_search"
    META_FETCH = "meta_fetch"
    META_EXECUTE = "meta_execute"
    DIRECT_EXECUTE = "direct_execute"
    UNKNOWN = "unknown"
