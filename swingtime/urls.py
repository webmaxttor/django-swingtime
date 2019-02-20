from django.conf.urls import url
from . import views, models, utils


urlpatterns = utils.make_urlpatterns(
    views,
    models.Event,
    models.Occurrence,
    models.EventType
)
