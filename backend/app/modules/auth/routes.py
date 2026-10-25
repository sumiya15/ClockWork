from fastapi import APIRouter, Depends, Request, Response
from . import service
from .guards import COOKIE, access_token, current_user, csrf_guard
from .schemas import LoginInput, LoginView, LogoutView, UserView, public_user

router = APIRouter(prefix='/api/v1/auth', tags=['Authentication'])


@router.post('/login', response_model=LoginView, dependencies=[Depends(csrf_guard)])
def login(body: LoginInput, request: Request, response: Response):
    settings = request.app.state.settings
    result, token = service.login(request.app.state.db, settings, body, request.state.correlation_id,
                                  request.cookies.get(COOKIE))
    response.set_cookie(COOKIE, token, httponly=True, secure=settings.cookie_secure,
                        samesite='strict', path='/api/v1', max_age=settings.session_minutes * 60)
    return result


@router.get('/me', response_model=UserView)
def me(user=Depends(current_user)):
    return public_user(user)


@router.post('/logout', response_model=LogoutView, dependencies=[Depends(csrf_guard)])
def logout(request: Request, response: Response, token=Depends(access_token)):
    service.logout(request.app.state.db, token, request.state.correlation_id)
    response.delete_cookie(COOKIE, path='/api/v1', httponly=True,
                           secure=request.app.state.settings.cookie_secure, samesite='strict')
    return LogoutView()
