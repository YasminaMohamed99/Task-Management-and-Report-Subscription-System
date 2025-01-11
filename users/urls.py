from django.urls import path
from users.views.sign_up import SignUpView
from users.views.sign_in import SignInView, TokenRefreshViewWithCustomResponse

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('token/refresh/', TokenRefreshViewWithCustomResponse.as_view(), name='token_refresh'),

]
