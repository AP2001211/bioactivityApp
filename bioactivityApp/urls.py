
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings
from . import views




urlpatterns = [
    path('admin/', admin.site.urls),
    path('aromataseFile/', include('aromatase.urls')),
    path('alkFile/', include('ALK.urls')),
    path('mTORFile/', include('mTOR.urls')),
    path('PI3KFile/', include('PI3K.urls')),
    path('team', views.team),
    path('visual', views.visual),
    path('', views.index, name = 'index'),
]
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
