class OpenFigiError(Exception):
    ...


class HTTPError(OpenFigiError):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP error {self.status_code}: {self.message}")


class TooManyMappingJobs(OpenFigiError):
    ...


class FilterQueryError(OpenFigiError):
    ...
