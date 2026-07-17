from fastapi import HTTPException, status


class HttpError:
    @staticmethod
    def raise_error(status_code: int, detail: str) -> None:
        raise HTTPException(status_code=status_code, detail=detail)

    @classmethod
    def unauthorized(cls, detail: str = 'Not authenticated') -> None:
        cls.raise_error(status.HTTP_401_UNAUTHORIZED, detail)

    @classmethod
    def forbidden(cls, detail: str = 'Insufficient permissions') -> None:
        cls.raise_error(status.HTTP_403_FORBIDDEN, detail)

    @classmethod
    def conflict(cls, detail: str) -> None:
        cls.raise_error(status.HTTP_409_CONFLICT, detail)

    @classmethod
    def not_found(cls, detail: str = 'Not found') -> None:
        cls.raise_error(status.HTTP_404_NOT_FOUND, detail)

    @classmethod
    def bad_request(cls, detail: str) -> None:
        cls.raise_error(status.HTTP_400_BAD_REQUEST, detail)