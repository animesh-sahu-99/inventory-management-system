from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import get_auth_service, get_current_user, require_admin
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserOut, UserRoleUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.register(data)


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate(form.username, form.password)
    return Token(access_token=auth_service.create_token(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserOut])
def list_users(
    _: User = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.list_users()


@router.patch("/users/{user_id}/role", response_model=UserOut)
def change_role(
    user_id: int,
    data: UserRoleUpdate,
    _: User = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.update_role(user_id, data.role)
