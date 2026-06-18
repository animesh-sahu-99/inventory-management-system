from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, data: UserCreate) -> User:
        if self.user_repo.get_by_email(data.email):
            raise ConflictError("Email already registered")
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=UserRole.staff,
        )
        self.user_repo.add(user)
        self.user_repo.commit()
        self.user_repo.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError()
        return user

    def create_token(self, user: User) -> str:
        return create_access_token({"sub": str(user.id), "role": user.role.value})

    def list_users(self) -> list[User]:
        return self.user_repo.list_all()

    def update_role(self, user_id: int, role: UserRole) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        user.role = role
        self.user_repo.commit()
        self.user_repo.refresh(user)
        return user
