from django.urls import path, include

app_name = 'api-v1'

urlpatterns = [
    # accounts urls
    path('accounts/', include('accounts.urls_api_v1', namespace='accounts')),

]
