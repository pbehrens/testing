from django.conf.urls.defaults import *


urlpatterns = patterns('radio.frontend.views',
    url(r'^$', 'home', name='home'),
    # url(r'^csv/$', 'csv', name='csv'),
)
