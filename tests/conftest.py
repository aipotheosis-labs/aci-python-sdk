from typing import Generator

import pytest

from aipolabs import Aipolabs

from .utils import API_KEY, BASE_URL


@pytest.fixture(scope="session")
def client() -> Generator[Aipolabs, None, None]:
    with Aipolabs(api_key=API_KEY, base_url=BASE_URL) as client:
        yield client
