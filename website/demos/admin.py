from django.contrib import admin
from django import forms

from .models import Game, Website, Source, Language, Magazine, Country

class WebsiteInline(admin.StackedInline):
    model = Website
    extra = 0

class SourceInline(admin.StackedInline):
    model = Source.game.through
    extra = 0

class GameAdmin(admin.ModelAdmin):
    def downloads(self, game): 
        d, _ = game.download_set.get_or_create() 
        return d.downloads
    def plays(self,game):
        p, _ = game.play_set.get_or_create()
        return p.plays
    downloads.admin_order_field = "download__downloads"
    plays.admin_order_field = "play__plays"
    list_display= ["game", "downloads", "plays"]
    prepopulated_fields = {"slug": ("game",)}
    inlines=[SourceInline, WebsiteInline]

class SourceAdminForm(forms.ModelForm):
    game = forms.ModelMultipleChoiceField(queryset=Game.objects.order_by('slug'), required=False, widget=forms.SelectMultiple(attrs={'size': 20}))

class SourceAdmin(admin.ModelAdmin):
    def explores(self,source):
        e, _ = source.explore_set.get_or_create()
        return e.explores
    explores.admin_order_field = "explore__explores"
    list_display=["description", "magazine", "explores", "disc", "volume", "issue_number", "month", "year"]
    prepopulated_fields = {"slug": ["description",]}
    form = SourceAdminForm

class LanguageAdmin(admin.ModelAdmin):
    pass

class CountryAdmin(admin.ModelAdmin):
    list_display=["name", "iso", "icon", "display_order"]

class MagazineAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["magazine",]}

admin.site.register(Game, GameAdmin)
admin.site.register(Magazine, MagazineAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Language,LanguageAdmin)
admin.site.register(Country, CountryAdmin)