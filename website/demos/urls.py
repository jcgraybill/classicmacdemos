from django.urls import path
from demos.feeds import LatestEntriesFeed, LatestEntriesWithImagesFeed
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from demos.models import Game, Magazine, Source

from . import views
app_name = "demos"

gamelist = {
    "queryset": Game.objects.all(),
    "date_field": "added"
}

sourcelist = {
    "queryset": Source.objects.all(),
    "date_field": "added"
}

magazinelist = {
    "queryset": Magazine.objects.all()
}

urlpatterns = [
    path("", views.home, name="home"),
    path("games/", views.GameListView.as_view(), kwargs={ "order": "game" }, name="games"),
    path("nn/games/", views.GameListView.as_view(), kwargs={ "order": "game", "nonav": "true" }, name="games_nn"),
    path("playable/", views.GameListView.as_view(), kwargs={ "order": "game", "constraint": "playable" }, name="playable"),
    path("play/<slug:slug>/", views.play, name="play"),
    path("<slug:slug>", views.DemoView.as_view(), name="demo"),
    path("download/<slug:slug>/", views.download, { "mc68k": False }, name="download"),
    path("download/alt/<slug:slug>/", views.download, { "mc68k": True }, name="download/68k"),
    path("explore/<slug:slug>/", views.explore, { "alt": False, "osx": False }, name="explore"),
    path("explore/osx/<slug:slug>/", views.explore, { "alt": False, "osx": True }, name="explore/osx"),
    path("explore/alt/<slug:slug>/", views.explore, { "alt": True, "osx": False }, name="explore/alt"),
    path("explore/alt/osx/<slug:slug>/", views.explore, { "alt": True, "osx": True  }, name="explore/alt/osx"),
    path("discs/", views.MagazineListView.as_view(), name="sources"),
    path("nn/discs/", views.MagazineListView.as_view(), kwargs={ "nonav": "true" }, name="sources_nn"),
    path("disc/<slug:slug>/", views.SourceView.as_view(), name="source"),
    path("about/", views.about, name="about"),
    path("rss/", LatestEntriesFeed(), name="rss"),
    path("rss/withimages/", LatestEntriesWithImagesFeed(), name="rsswithimages"),
    path("sitemap.xml", sitemap, { "sitemaps": { 
                                    "games": GenericSitemap(gamelist, protocol="https"),
                                    "magazines": GenericSitemap(magazinelist, protocol="https"),
                                    "discs": GenericSitemap(sourcelist, protocol="https")
                                    }
                                   }, name="django.contrib.sitemaps.views.sitemap"),
    path("magazine/<slug:slug>/", views.MagazineView.as_view(), name="magazine"),
    path("classicmacdemos.css", views.css, name="css"),
]