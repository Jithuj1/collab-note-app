from django.urls import path

# local imports
from note.views.home import home_view, login_view

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
]