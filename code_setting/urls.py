from django.apps import apps
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from apps.core.admin import CORE_MODELS_ADMIN
from apps.core.routers import core_router, core_datacenter_router

from code_setting.settings import DATABASES, MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT, BASE_URL, LOCAL_APPLICATIONS

schema_view = get_schema_view(
    openapi.Info(
        title="codifo fuente v1.0 - APIs Docs",
        default_version='v1',
        description="REST APIs for  platform",
        terms_of_service="https://www.company.com",
        contact=openapi.Contact(email="info@code_setting.com"),
        license=openapi.License(name="BSD License"),
    ),
    url=BASE_URL,
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [

    # Homepage
    # path('', views.index, name='index'),

    # Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Docs (swagger and redoc)
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

# Dynamic URLs for Master
master_site_id = admin.AdminSite('default')
for model_obj in apps.get_app_config('xmaster').get_models():
    model_admin = MASTER_MODELS_ADMIN.get(model_obj.__name__, '')
    if model_admin:
        master_site_id.register(model_obj, model_admin)

urlpatterns += [

    # Master Django Admin
    path('master/admin/', master_site_id.urls, name='master-admin'),

    # Master APIs
    path('master/', include(master_router.urls)),
]

# Dynamic URLs for Companies per apps
for company in [k for k in DATABASES.keys() if k != 'default']:

    # django admin register
    company_site_id = admin.AdminSite(company)

    for app in LOCAL_APPLICATIONS:

        if app == 'core':
            admin_dict = CORE_MODELS_ADMIN
        else:
            admin_dict = None

        if admin_dict:
            for model_obj in apps.get_app_config(app).get_models():
                company_site_id.register(model_obj, admin_dict[model_obj.__name__])

    urlpatterns += [

        # Companies Django admin
        path(f'{company}/admin/', company_site_id.urls, name=f'{company}-admin'),

        # Companies APIs
        path(f'{company}/core/', include(core_router.urls)),
        path(f'{company}/core/', include(core_datacenter_router.urls)),

    ]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
