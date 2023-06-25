from django.shortcuts import redirect,render,get_object_or_404
from django.views import generic
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models import Q

from .models import Game, Source, Magazine, Country
from django.db.models.functions import Lower

from datetime import date

class GameListView(generic.ListView):
    context_object_name = "game_list"
    def get_queryset(self):
        order = "-added"
        orders = {"added": "added",
                  "-added": "-added",
                  "year": "year",
                  "-year": "-year",
                  "game": "slug",   # I don't love this hack for case/punctuation insensitive sorting
                  "-game": "-slug"}
        if 'constraint' in self.kwargs and self.kwargs['constraint'] == 'playable':
            return Game.objects.exclude( Q(infinite_mac_machine='') & Q(infinite_mac_custom_image='')).order_by('slug')
        else:
            if self.kwargs['order'] in orders.keys():
                order = orders[self.kwargs['order']]
            return Game.objects.order_by(order)

class DemoView(generic.DetailView):
    model = Game
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["screens"] = range(1,self.get_object().screens + 1)
        return context

class SourceView(generic.DetailView):
    model = Source
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["images"] = range(1,self.get_object().images + 1)
        context["tab"] = "discs"
        return context

class MagazineListView(generic.ListView):
    model = Magazine
    def get_queryset(self):
        return Magazine.objects.order_by('slug')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tab"] = "discs"
        context["countries"] = Country.objects.order_by("display_order", "iso")
        return context

class MagazineView(generic.DetailView):
    model = Magazine
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tab"] = "discs"
        return context
    
def download(request, slug, mc68k):
    prefix = request.scheme +  "://download.classicmacdemos.com/"
    game = get_object_or_404(Game, slug=slug)
    d, _ = game.download_set.get_or_create()
    d.downloads +=1
    d.save()
    filename = game.filename
    if mc68k and game.filename_68k:
        filename = game.filename_68k
    return redirect(prefix + filename)

def play(request,slug):
    game = get_object_or_404(Game, slug=slug)
    if game.infinite_mac_custom_image != '':
        url = "https://infinitemac.org/run?cdrom=https://img.classicmacdemos.com/{slug}.dsk&machine={infinite_mac_custom_image}&saved_hd=true".format(
            infinite_mac_custom_image = game.infinite_mac_custom_image,
            slug = slug
        )
        p, _ = game.play_set.get_or_create()
        p.plays += 1
        p.save()
        return redirect(url)
    elif game.infinite_mac_machine != '':
        url = "https://infinitemac.org/{infinite_mac_machine}&cdroms=true&cdrom_url=https://img.classicmacdemos.com/{slug}.img&saved_hd=true".format(
            infinite_mac_machine = game.infinite_mac_machine,
            slug = slug
        )
        p, _ = game.play_set.get_or_create()
        p.plays += 1
        p.save()
        return redirect(url)
    else:
        return HttpResponseNotFound()

def explore(request, slug: str, alt: bool, osx: bool):
    source = get_object_or_404(Source, slug=slug)
    infinite_mac_machine = source.infinite_mac_osx_machine if osx else source.infinite_mac_machine
    infinite_mac_url = source.disc2_infinite_mac_url if alt else source.infinite_mac_url
    
    if not (infinite_mac_machine and infinite_mac_url): 
        return HttpResponseNotFound()

    e, _ = source.explore_set.get_or_create()
    e.explores += 1
    e.save()

    url = "https://infinitemac.org/{infinite_mac_machine}&cdroms=true&cdrom_url={infinite_mac_url}&saved_hd=true".format(
        infinite_mac_machine = infinite_mac_machine,
        infinite_mac_url = infinite_mac_url
    )

    return redirect(url)


def about(request):
    context = dict()
    context["count"] = Game.objects.count()
    context["sources"] = Source.objects.count()
    context["infinitemac"] = Game.objects.exclude( Q(infinite_mac_machine='') & Q(infinite_mac_custom_image='')).order_by("-play__plays")
    context["screenshots"] = Game.objects.exclude(screens__gte=1).order_by("slug")
    context["single_screenshot"] = Game.objects.filter(screens__exact=1).order_by("slug")
    context["blurb"] = Game.objects.filter(blurb__exact='').order_by("slug")
    context["playable"] = Game.objects.filter( Q(infinite_mac_machine='') & Q(infinite_mac_custom_image='')).order_by("slug")
    context["custom_image"] = Game.objects.exclude(Q(infinite_mac_machine='')).order_by("slug")
    return render(request, "demos/about.html", context)

def home(request):
    context = dict()
    context["recent"] = Game.objects.order_by("-added")
    context["downloads"] = Game.objects.all().order_by("-download__downloads")
    context["infinitemac"] = Game.objects.exclude( Q(infinite_mac_machine='') & Q(infinite_mac_custom_image='')).order_by("-play__plays")
    featured = Game.objects.filter(screens__gte=1).exclude(blurb__exact='').exclude(infinite_mac_custom_image__exact='')
    datesum = date.today().year + date.today().month + date.today().day
    context["featured"] = featured[datesum % featured.count()]
    context["discs"] = Source.objects.order_by('-added')
    return render(request,"demos/home.html", context)

def css(request):
    return HttpResponse(
        render(request, "demos/classicmacdemos.css", {}),
        headers={
         "Content-Type": "text/css",
        }
    )