"""DevilAnalysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from main import views as main_view
from django.contrib.auth import views as auth

urlpatterns = [

    path('admin/', admin.site.urls),

    ##### user related path##########################
    path('', include('main.urls')),
    path('login/', main_view.Login, name='login'),
    path('logout/', auth.LogoutView.as_view(template_name='main/index.html'), name='logout'),
    path('register/', main_view.register, name='register'),
    path('overview/', main_view.Overview, name='overview'),
    path('portfolio/', main_view.portfolio, name='portfolio'),
    path('sell/', main_view.sell, name='sell'),
    path('purchase/', main_view.purchase, name='purchase'),
    path('profile/', main_view.profile, name='profile'),
    path('analysis/', main_view.analysis, name='analysis'),
]
