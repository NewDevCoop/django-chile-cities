from django.contrib import admin

from django_chile_cities.models import City, Province, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "code", "iso_3166_2_cl"]
    search_fields = ["name", "iso_3166_2_cl"]
    ordering = ["number"]


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ["name", "region", "code"]
    list_filter = ["region"]
    search_fields = ["name"]
    autocomplete_fields = ["region"]
    list_select_related = ["region"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "province", "code", "conara_sii"]
    list_filter = ["province__region"]
    search_fields = ["name", "hashtag"]
    autocomplete_fields = ["province"]
    list_select_related = ["province", "province__region"]
