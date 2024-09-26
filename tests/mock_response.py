class MockResponse:
    """Class used for return mocked async aio response"""

    def __init__(self, json, status):
        self._json = json
        self.status = status

    async def json(self):
        return self._json

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self
