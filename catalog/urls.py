from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import (
    CatalogDetailView,
    CatalogListViews,
    ContactView,
    ProductCreateView,
)

app_name = CatalogConfig.name

urlpatterns = [
    path("", CatalogListViews.as_view(), name="product_list"),
    path("contacts/", ContactView.as_view(), name="contacts"),
    path(
        "product_detail/<int:pk>/", CatalogDetailView.as_view(), name="product_detail"
    ),
    path("product_create/", ProductCreateView.as_view(), name="product_create"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
