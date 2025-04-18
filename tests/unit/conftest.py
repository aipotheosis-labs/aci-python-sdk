from typing import Generator

import pytest

from aci import ACI

from .utils import MOCK_API_KEY, MOCK_BASE_URL


@pytest.fixture(scope="session")
def client() -> Generator[ACI, None, None]:
    with ACI(api_key=MOCK_API_KEY, base_url=MOCK_BASE_URL) as client:
        yield client
