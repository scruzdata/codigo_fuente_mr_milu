from rest_framework_nested import routers

from apps.core.viewsets import (FeedbackViewSet, DynamicHelpViewSet, EventViewSet,
                                EventSearchesViewSet, TableViewSet)

core_router = routers.SimpleRouter()

core_router.register(r'feedbacks', FeedbackViewSet, basename='feedbacks')
core_router.register(r'dynamic-help', DynamicHelpViewSet, basename='dynamic-help')

# Datacenters nested viewsets
core_router.register(r'table', TableViewSet, basename='table')
core_datacenter_router = routers.NestedSimpleRouter(core_router, r'table', lookup='table')
core_datacenter_router.register(r'events', EventViewSet, basename='events')
core_datacenter_router.register(r'events-searches', EventSearchesViewSet, basename='events-searches')

