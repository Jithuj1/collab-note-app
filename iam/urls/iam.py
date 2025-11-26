from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

# local imports
from iam.views.auth import EmailTokenObtainPairView
from iam.views.users import UserListView

urlpatterns = [
    path('token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user_list'),
]