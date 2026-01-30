from django.shortcuts import redirect,render,get_object_or_404
from django.views import generic
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models import Q
from django.urls import reverse

from .models import Game, Source, Magazine, Country
from django.db.models.functions import Lower

from datetime import date

class GameListView(generic.ListView):
    context_object_name = "game_list"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["canonical_uri"] = self.request.build_absolute_uri(reverse("demos:games"))
        return context
    def get_queryset(self):
        order = "-added"
        orders = {"added": "added",
                  "-added": "-added",
                  "year": "year",
                  "-year": "-year",
                  "game": "slug",   # I don't love this hack for case/punctuation insensitive sorting
                  "-game": "-slug"}
        if 'constraint' in self.kwargs and self.kwargs['constraint'] == 'playable':
            return Game.objects.filter(virtual_machine__isnull=False).order_by('slug')
        else:
            if self.kwargs['order'] in orders.keys():
                order = orders[self.kwargs['order']]
            return Game.objects.order_by(order)

class DemoView(generic.DetailView):
    model = Game
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["screens"] = range(1,self.get_object().screens + 1)
        context["canonical_uri"] = self.request.build_absolute_uri(self.get_object().get_absolute_url())
        return context

class SourceView(generic.DetailView):
    model = Source
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["images"] = range(1,self.get_object().images + 1)
        context["tab"] = "discs"
        context["canonical_uri"] = self.request.build_absolute_uri(self.get_object().get_absolute_url())
        return context

class MagazineListView(generic.ListView):
    model = Magazine
    def get_queryset(self):
        return Magazine.objects.order_by('slug')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tab"] = "discs"
        context["countries"] = Country.objects.order_by("display_order", "iso")
        context["canonical_uri"] = self.request.build_absolute_uri(reverse("demos:sources"))
        return context

class MagazineView(generic.DetailView):
    model = Magazine
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tab"] = "discs"
        context["canonical_uri"] = self.request.build_absolute_uri(self.get_object().get_absolute_url())
        return context
    
def download(request, slug, dl: int):
    prefix = request.scheme +  "://download.classicmacdemos.com/"
    game = get_object_or_404(Game, slug=slug)
    d, _ = game.download_set.get_or_create()
    d.downloads +=1
    d.save()
    if dl == 2 and game.filename_68k:
        filename = game.filename_68k
    elif dl == 3 and game.filename_3:
        filename = game.filename_3
    else:
        filename = game.filename
    return redirect(prefix + filename)

def play(request,slug):
    game = get_object_or_404(Game, slug=slug)
    if game.virtual_machine:
        url = "https://infinitemac.org/embed?disk_url=https://img.classicmacdemos.com/{slug}.dsk&machine={virtual_machine}".format(
            virtual_machine = game.virtual_machine.machine,
            slug = slug
        )
        p, _ = game.play_set.get_or_create()
        p.plays += 1
        p.save()
        return redirect(url)
    else:
        return HttpResponseNotFound()

def explore(request, slug: str, disc: int, osx: bool):
    source = get_object_or_404(Source, slug=slug)
    virtual_machine = source.osx_virtual_machine if osx else source.virtual_machine
    if disc == 2 and source.disc2_infinite_mac_url:        
        cdrom_url = source.disc2_infinite_mac_url
    elif disc == 3 and source.disc3_infinite_mac_url:        
        cdrom_url = source.disc3_infinite_mac_url
    elif disc == 4 and source.disc4_infinite_mac_url:        
        cdrom_url = source.disc4_infinite_mac_url
    else:
        cdrom_url = source.infinite_mac_url
    
    if not (virtual_machine and cdrom_url): 
        return HttpResponseNotFound()

    e, _ = source.explore_set.get_or_create()
    e.explores += 1
    e.save()

    url = "https://infinitemac.org/embed?machine={virtual_machine}&disk={virtual_machine_disk}&cdrom={cdrom_url}&infinite_hd=true".format(
        virtual_machine = virtual_machine.machine,
        virtual_machine_disk = virtual_machine.disk,
        cdrom_url = cdrom_url
    )

    return redirect(url)

def about(request):
    context = dict()
    context["canonical_uri"] = request.build_absolute_uri(reverse("demos:about"))
    context["count"] = Game.objects.count()
    context["sources"] = Source.objects.exclude(disc2_infinite_mac_url__exact='').count() + Source.objects.count()
    context["infinitemac"] = Game.objects.filter(virtual_machine__isnull=False).count()
    return render(request, "demos/about.html", context)

def home(request):
    context = dict()
    context["canonical_uri"] = request.build_absolute_uri(reverse("demos:home"))
    context["downloads"] = Game.objects.order_by("-download__downloads")
    context["infinitemac"] = Game.objects.filter(virtual_machine__isnull=False).order_by("-play__plays")
    context["discs"] = Source.objects.order_by('-added')
    context["sources"] = Source.objects.exclude(disc2_infinite_mac_url__exact='').count() + Source.objects.count()
    return render(request,"demos/home.html", context)

def css(request):
    return HttpResponse(
        render(request, "demos/classicmacdemos.css", {}),
        headers={
         "Content-Type": "text/css",
        }
    )