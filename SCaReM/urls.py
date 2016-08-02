"""SCaReM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import views, views_schedule, views_crud

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^logs$', views.log),
    url(r'^logs/(?P<year>[0-9]{4})$', views.log),
    url(r'^logs/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$', views.log),
    url(r'^logs/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})$', views.log),

    url(r'^reservation/create/', views_crud.create_or_edit_reservation),
    url(r'^reservation/edit/(?P<reservation_id>[0-9]+)/$', views_crud.create_or_edit_reservation),
    url(r'^reservation/delete/(?P<reservation_id>[0-9]+)/$', views_crud.delete_reservation),

    url(r'^schedule/bycamp/', views_schedule.view_by_camp),
    url(r'^schedule/byresource/', views_schedule.view_by_resource),
    url(r'^schedule/bydate/', views_schedule.view_by_date),
]
