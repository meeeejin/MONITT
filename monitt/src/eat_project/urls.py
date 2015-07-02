from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static

from endless_pagination.views import AjaxListView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'signup.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^signup/$', 'signup.views.signup', name='signup'),
    url(r'^signup_success/$', 'signup.views.signup_success', name='signup_success'),
    url(r'^signin/$', 'signup.views.signin', name='signin'),
    url(r'^auth/$', 'signup.views.auth_view', name='auth_view'),
    url(r'^dashboard/signout/$', 'dashboard.views.signout', name='signout'),
    url(r'^invalid/$', 'signup.views.invalid_signin', name='invalid_signin'),
    url(r'^dashboard/$', 'dashboard.views.dashboard', name='dashboard'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dashboard/create_test/$', 'dashboard.views.create_test', name='create_test'),
    url(r'^dashboard/alltests/$', 'dashboard.views.alltests', name='alltests'),
    url(r'^dashboard/notification_tests/$', 'dashboard.views.notification_tests', name='notification_tests'),
    url(r'^dashboard/scheduling_tests/$', 'dashboard.views.scheduling_tests', name='scheduling_tests'),
    url(r'^dashboard/errors/$', 'dashboard.views.errors', name='errors'),
    url(r'^dashboard/guide/$', 'dashboard.views.guide', name='guide'),
    url(r'^dashboard/settings/$', 'dashboard.views.settings', name='settings'),
    url(r'^dashboard/delete_test/$', 'dashboard.views.delete_test', name='delete_test'),
    url(r'^dashboard/delete_file/$', 'dashboard.views.delete_file', name='delete_file'),
    url(r'^dashboard/delete_noti/$', 'dashboard.views.delete_noti', name='delete_noti'),
    url(r'^dashboard/delete_sche/$', 'dashboard.views.delete_sche', name='delete_sche'),
    url(r'^dashboard/run_test/$', 'dashboard.views.run_test', name='run_test'),
    url(r'^dashboard/alltestresults_search/$', 'dashboard.views.alltestresults_search', name='alltestresults_search'),
    url(r'^dashboard/schedulings_search/$', 'dashboard.views.schedulings_search', name='schedulings_search'),
    url(r'^dashboard/notifications_search/$', 'dashboard.views.notifications_search', name='notifications_search'),
    url(r'^dashboard/errors_search/$', 'dashboard.views.errors_search', name='errors_search'),
    url(r'^dashboard/alltests_search/$', 'dashboard.views.alltests_search', name='alltests_search')
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
