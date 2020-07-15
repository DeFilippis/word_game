from django.conf.urls import url

from views import update_counter

urlpatterns = [
   url(r'^update_counter/', update_counter)
]