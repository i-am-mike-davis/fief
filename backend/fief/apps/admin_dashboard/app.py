from fastapi import Depends, FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from fief.apps.admin_dashboard.dependencies import BaseContext, get_base_context
from fief.apps.admin_dashboard.routers.api_keys import router as api_keys_router
from fief.apps.admin_dashboard.routers.auth import router as auth_router
from fief.apps.admin_dashboard.routers.clients import router as clients_router
from fief.apps.admin_dashboard.routers.tenants import router as tenants_router
from fief.apps.admin_dashboard.routers.workspaces import router as workspaces_router
from fief.middlewares.csrf import CSRFCookieSetterMiddleware
from fief.paths import STATIC_DIRECTORY
from fief.settings import settings
from fief.templates import templates

app = FastAPI(title="Fief Administration Dashboard", openapi_url=None)

app.add_middleware(CSRFCookieSetterMiddleware)
app.add_middleware(GZipMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret.get_secret_value(),
    session_cookie=settings.session_data_cookie_name,
    max_age=settings.session_data_cookie_lifetime_seconds,
    https_only=settings.session_data_cookie_secure,
)

app.include_router(api_keys_router, prefix="/api-keys")
app.include_router(auth_router, prefix="/auth")
app.include_router(clients_router, prefix="/clients")
app.include_router(tenants_router, prefix="/tenants")
app.include_router(workspaces_router, prefix="/workspaces")
app.mount(
    "/static", StaticFiles(directory=STATIC_DIRECTORY), name="admin_dashboard:static"
)


@app.get("/")
async def index(context: BaseContext = Depends(get_base_context)):
    return templates.TemplateResponse("admin/index.html", {**context})


__all__ = ["app"]
