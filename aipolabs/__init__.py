from aipolabs.client import Aipolabs
from aipolabs.enums.app import App
from aipolabs.enums.function import Function
from aipolabs.enums.function_call_type import AipolabsFunctionCallType
from aipolabs.meta_functions.execute_function import AIPOLABS_EXECUTE_FUNCTION
from aipolabs.meta_functions.get_function_definition import (
    AIPOLABS_GET_FUNCTION_DEFINITION,
)
from aipolabs.meta_functions.search_apps import AIPOLABS_SEARCH_APPS
from aipolabs.meta_functions.search_functions import AIPOLABS_SEARCH_FUNCTIONS
from aipolabs.utils.logging import setup_logging as _setup_logging

_setup_logging()

__all__ = [
    "App",
    "Function",
    "Aipolabs",
    "AIPOLABS_GET_FUNCTION_DEFINITION",
    "AIPOLABS_SEARCH_APPS",
    "AIPOLABS_SEARCH_FUNCTIONS",
    "AIPOLABS_EXECUTE_FUNCTION",
    "AipolabsFunctionCallType",
]
