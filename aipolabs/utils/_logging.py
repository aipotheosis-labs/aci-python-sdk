import logging
import os
import shutil

from typing_extensions import override

from aipolabs.utils._type_check import is_dict

logger: logging.Logger = logging.getLogger("aipolabs")
httpx_logger: logging.Logger = logging.getLogger("httpx")


SENSITIVE_HEADERS = {"x-api-key", "authorization"}
AIPOLABS_LOG_LEVEL = os.environ.get("AIPOLABS_LOG_LEVEL", "warn")


def setup_logging() -> None:
    logging.basicConfig(
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    httpx_logger.setLevel(logging.WARN)
    # TODO: avoid logging any sensitive headers
    logger.addFilter(SensitiveHeadersFilter())

    if AIPOLABS_LOG_LEVEL == "debug":
        logger.setLevel(logging.DEBUG)
    elif AIPOLABS_LOG_LEVEL == "info":
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARN)


class SensitiveHeadersFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        if is_dict(record.args):
            headers = record.args.get("headers")
            if is_dict(headers):
                headers = record.args["headers"] = {**headers}
                for header in headers:
                    if str(header).lower() in SENSITIVE_HEADERS:
                        headers[header] = "<redacted>"
        return True


def create_headline(title: str, fill_char: str = "-") -> str:
    """Create a header that fills the terminal width with the given title centered.

    Args:
        title: The text to center in the header
        fill_char: The character to use for filling (default: "-")

    Returns:
        A string containing the formatted header with green title text
    """
    # ANSI escape codes for green text and reset
    GREEN = "\033[32m"
    RESET = "\033[0m"

    terminal_width = shutil.get_terminal_size().columns or 80
    padded_title = f" {GREEN}{title}{RESET} "  # Add green color to title
    padding = fill_char * ((terminal_width - len(title) - 2) // 2)  # -2 for the spaces
    header = f"{padding}{padded_title}{padding}"

    # Add extra fill_char if the total length is off by one due to integer division
    if len(header) - len(GREEN) - len(RESET) < terminal_width:
        header += fill_char

    return header
