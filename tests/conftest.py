from typing import Generator

import pytest

from aipolabs import Aipolabs

from .utils import BASE_URL, MOCK_API_KEY


@pytest.fixture(scope="session")
def client() -> Generator[Aipolabs, None, None]:
    with Aipolabs(api_key=MOCK_API_KEY, base_url=BASE_URL) as client:
        yield client
