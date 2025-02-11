from typing import Generator

import pytest

from aipolabs import Aipolabs

from .utils import MOCK_API_KEY, MOCK_BASE_URL


@pytest.fixture(scope="session")
def client() -> Generator[Aipolabs, None, None]:
    with Aipolabs(api_key=MOCK_API_KEY, base_url=MOCK_BASE_URL) as client:
        yield client
