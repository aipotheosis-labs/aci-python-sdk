import logging
import os

from typing_extensions import override

from aipolabs.utils.type_check import is_dict

logger: logging.Logger = logging.getLogger("aipolabs")
httpx_logger: logging.Logger = logging.getLogger("httpx")


SENSITIVE_HEADERS = {"x-api-key", "authorization"}
AIPOLABS_LOG_LEVEL = os.environ.get("AIPOLABS_LOG_LEVEL", "info")


def setup_logging() -> None:
    logging.basicConfig(
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if AIPOLABS_LOG_LEVEL == "debug":
        logger.setLevel(logging.DEBUG)
        httpx_logger.setLevel(logging.DEBUG)
    elif AIPOLABS_LOG_LEVEL == "info":
        logger.setLevel(logging.INFO)
        httpx_logger.setLevel(logging.INFO)


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
