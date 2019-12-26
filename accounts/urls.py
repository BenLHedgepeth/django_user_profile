from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'sign_in/$', views.sign_in, name='sign_in'),
    url(r'sign_up/$', views.sign_up, name='sign_up'),
    url(r'sign_out/$', views.sign_out, name='sign_out'),
    url(r'profile/(?P<user_id>\d+)/$', views.profile, name='profile'),
    url(
        r'profile_create/(?P<user_id>\d+)/$',
        views.new_profile, name="new_profile"
    ),
    url(
        r'profile_edit/(?P<user_id>\d+)/$',
        views.edit_profile, name="edit_profile"
    ),
    url(
        r'profile/change_password/(?P<user_id>\d+)/$',
        views.change_password, name="change_password"
    )
]
