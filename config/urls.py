"""URL configuration: mounts the Ninja API under /api/."""

from django.urls import path
from ninja import NinjaAPI

from accounts.api import router as accounts_router
from bookmarks.api import router as bookmarks_router

api = NinjaAPI(title="Bookmarks API", version="1.0.0")
api.add_router("/auth", accounts_router)
api.add_router("/bookmarks", bookmarks_router)

urlpatterns = [
    path("api/", api.urls),
]
