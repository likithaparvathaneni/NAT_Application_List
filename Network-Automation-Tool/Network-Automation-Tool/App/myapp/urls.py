from django.urls import path
from .views import (
    home, home_check, firewall, firewall_update, fw_firewall, zones,
    resolve_fqdn_to_ip, fetch_all_apps, Add, Firewall_names, App,
    check_object, create_object, check_object_name, check_service, create_service,
    search_address_group, list_address_objects, create_address_group, check_address_group_name,
    list_address_groups, list_service_groups, search_service_group, list_service_objects,
    create_service_group, check_service_group_name, firewall_hierarchy_api, list_applications,create_security_rule_api, check_service_group_name,
)

from Compare_final.AddingRule import list_service_objects_api
from Compare_final.security_profiles import  list_security_profiles_api

urlpatterns = [
    path('home/', home, name='home'),
    path('home_check/', home_check, name='home_check'),
    path('firewall/', firewall, name='firewall'),
    path("firewall_fetch/", firewall_update, name="firewall_fetch"),
    path("firewall_search/", fw_firewall, name="firewall_search"),
    path("zones/", zones, name="zones"),
    path("apps/", fetch_all_apps, name="fetch_all_apps"),
    path("fqdn/", resolve_fqdn_to_ip, name="fqdn"),
    path("Add/", Add, name="add"),
    path("Firewall_name/", Firewall_names, name="Firewall_name"),
    path("App/", App, name="app"),
    
    # Object Checker URLs
    path('check_object/', check_object, name='check_object'),
    path('create_object/', create_object, name='create_object'),
    path('check_object_name/', check_object_name, name='check_object_name'),
    path('check_service/', check_service, name='check_service'),
    path('create_service/', create_service, name='create_service'),
    
    # Address Group URLs
    path('search_address_group/', search_address_group, name='search_address_group'),
    path('list_address_objects/', list_address_objects, name='list_address_objects'),
    path('create_address_group/', create_address_group, name='create_address_group'),
    path('check_address_group_name/', check_address_group_name, name='check_address_group_name'),
    path('list_address_groups/', list_address_groups, name='list_address_groups'),
    
    # Service Group URLs
    path('list_service_groups/', list_service_groups, name='list_service_groups'),
    path('search_service_group/', search_service_group, name='search_service_group'),
    path('list_service_objects/', list_service_objects, name='list_service_objects'),
    path('create_service_group/', create_service_group, name='create_service_group'),
    path('check_service_group_name/', check_service_group_name, name='check_service_group_name'),
    
    # Rule Management URLs
    path('firewall-hierarchy/', firewall_hierarchy_api, name='firewall_hierarchy'),
    path('create-rule/', create_security_rule_api, name='create_rule'),
    path('list_service_objects/', list_service_objects_api, name='list_service_objects'),
    path('list_security_profiles/', list_security_profiles_api, name='list_security_profiles'),
    path('list_applications/', list_applications, name='list_applications'),
]