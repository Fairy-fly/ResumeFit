from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthLoginRequest, AuthRegisterRequest, TokenResponse
from app.schemas.user import UserRead


class AuthError(Exception):
    pass


class EmailAlreadyRegisteredError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def register(self, payload: AuthRegisterRequest) -> TokenResponse:
        email = payload.email.strip().lower()
        existing_user = self.user_repository.get_by_email(email=email)
        if existing_user is not None:
            raise EmailAlreadyRegisteredError("Email is already registered.")

        user = self.user_repository.create(
            email=email,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name.strip(),
        )
        return self._build_token_response(user)

    def login(self, payload: AuthLoginRequest) -> TokenResponse:
        email = payload.email.strip().lower()
        user = self.user_repository.get_by_email(email=email)
        if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password.")

        if user.status != "active":
            raise InvalidCredentialsError("User is disabled.")

        return self._build_token_response(user)

    def _build_token_response(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id=user.id),
            token_type="bearer",
            user=UserRead.model_validate(user),
        )
