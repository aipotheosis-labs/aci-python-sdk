import logging

from aipolabs.utils.logging import SensitiveHeadersFilter

log: logging.Logger = logging.getLogger(__name__)
log.addFilter(SensitiveHeadersFilter())
