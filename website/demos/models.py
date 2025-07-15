from django.db import models
from django.urls import reverse
from django.db.models import Min, Max, Count, Q

import django, math, boto3

DEFAULT_MACHINE = ''
MACHINES = [
    ( DEFAULT_MACHINE, 'NONE' ),
    ( '1996/System 7.5.3?machine=Quadra+650', '68040 System 7.5.3' ),
    ( '1998/Mac OS 8.1?machine=Power+Macintosh+9500', 'PowerPC 604 Mac OS 8.1'),
    ( '1999/Mac OS 9.0?machine=Power+Macintosh+9500', 'PowerPC 604 Mac OS 9.0'),
    ( '2001/Mac OS X 10.1?machine=Power+Macintosh+G3+(Beige)', 'Mac OS X 10.1')
]
CUSTOM_IMAGE_MACHINES = [
    ( DEFAULT_MACHINE, 'NONE' ),
    ( 'Quadra+650', 'Quadra 650'),
    ( 'Power+Macintosh+9500&ram=32M', 'Power Macintosh 9500'),
    ( 'Power+Macintosh+9500&ram=64M', 'Power Macintosh 9500 64MB')
]

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

class Months(models.IntegerChoices):
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEPT = 9
    OCT = 10
    NOV = 11
    DEC = 12
    Holiday = 13

class VirtualMachine(models.Model):
    description = models.CharField("Description", max_length=50, blank=False)
    machine     = models.CharField("Machine configuration", max_length=100, blank=False)
    disk        = models.CharField("Disk name", max_length=50, blank=True)
    def __str__(self): return self.description

class Language(models.Model):
    name = models.CharField("Name", max_length=50, blank=False)
    iso  = models.CharField("ISO 639-1 Code", max_length=2, blank=False)
    icon = models.CharField("Icon", max_length=8, blank=False)
    def __str__(self): return self.name

class Country (models.Model):
    name = models.CharField("Name", max_length=50, blank=False)
    iso  = models.CharField("ISO 3166 Code", max_length=2, blank=False)
    icon = models.CharField("Icon", max_length=8, blank=False)
    display_order = models.IntegerField("Display order", blank=False, default=0)
    def __str__(self): return self.name

class Game(models.Model):
    s3 = boto3.client('s3')
    game = models.CharField("Game", max_length=200)
    aka  = models.CharField("aka", max_length=200, blank=True)
    contributor = models.CharField("Contributed by", max_length=200, blank=True)
    contributor_url = models.URLField("Contributor URL", blank=True)
    year = models.IntegerField("Published", default=2000)
    languages = models.ManyToManyField(Language, blank=True)
    filename = models.CharField("PowerPC/Universal file name", max_length=100)
    filename_68k = models.CharField("68k File name", max_length=100, blank=True)
    readme_txt = models.BooleanField("README.txt", default=False)
    readme_html = models.BooleanField("README.html", default=False)
    readme_pdf = models.BooleanField("README.pdf", default=False)
    added = models.DateTimeField("Added", default=django.utils.timezone.now)
    slug = models.SlugField(null=False, unique=True)
    screens = models.IntegerField("Screenshots", default=0)
    blurb = models.TextField("Blurb", blank=True)
    virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to=Q(disk__exact=''))
    infinite_mac_machine = models.CharField("Infinite Mac Prebuilt Machine", choices=MACHINES, max_length=200, blank=True, default=False)
    infinite_mac_custom_image = models.CharField("Infinite Mac Custom Image", choices=CUSTOM_IMAGE_MACHINES, max_length=200, blank=True, default=False)
    def __str__(self): return self.game
    def get_absolute_url(self): return reverse("demos:demo", kwargs={ "slug": self.slug })
    def get_sorted_sources(self): return self.source_set.all().order_by('description')
    def get_file_size(self): return self.getsize(self.filename)
    def get_alt_file_size(self): return self.getsize(self.filename_68k)
    def getsize(self, filename):
        try:
            head = self.s3.head_object(
                Bucket = "download.classicmacdemos.com",
                Key = filename
            )
            return convert_size(head["ContentLength"])
        except:
            return 0

class Magazine(models.Model):
    magazine = models.CharField("Magazine", max_length=200)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    url = models.URLField("Webpage", blank=True)
    slug = models.SlugField(null=False, unique=True)
    blurb = models.TextField("Blurb", blank=True)
    image = models.BooleanField("Has image?", default=False)
    def __str__(self): return self.magazine
    def begin(self): return self.source_set.aggregate(Min("year"))
    def end(self): return self.source_set.aggregate(Max("year"))
    def gamecount(self): return self.source_set.aggregate(Count("game"))
    def get_absolute_url(self): return reverse("demos:magazine", kwargs={ "slug": self.slug })
    def unique_game_count(self):
        games = dict()
        for disc in self.source_set.all():
            for game in disc.game.all():
                games[game] = True
        return len(games)

class Source(models.Model):
    game = models.ManyToManyField(Game, blank=True)
    magazine = models.ForeignKey(Magazine, null=True, on_delete=models.SET_NULL)
    description = models.CharField("Description", max_length=200)
    contributor = models.CharField("Contributed by", max_length=200, blank=True)
    contributor_url = models.URLField("Contributor URL", blank=True)
    url = models.URLField("Webpage", blank=True)
    magazine_url = models.URLField("Magazine URL", blank=True)
    magazine_embed_url = models.URLField("Embeddable Magazine URL", blank=True)
    infinite_mac_url = models.URLField("ISO/DMG URL", max_length=500, blank=True)
    virtual_machine = models.ForeignKey(VirtualMachine, related_name="source_virtual_machine", on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to=~Q(disk__exact=''))
    osx_virtual_machine = models.ForeignKey(VirtualMachine, related_name="source_osx_virtual_machine",on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mac OS X Virtual machine", limit_choices_to=~Q(disk__exact=''))
    infinite_mac_machine = models.CharField("Infinite Mac Machine", choices=MACHINES, max_length=200, blank=True, default=False)
    infinite_mac_osx_machine = models.CharField("Infinite Mac OS X Machine", choices=MACHINES, max_length=200, blank=True, default=False)
    year = models.IntegerField("Year", blank=True, default=2000, null=True)
    month = models.IntegerField("Month", blank=True, choices=Months.choices, default=None, null=True)
    disc = models.IntegerField("Disc #", blank=True, default=None, null=True)
    volume = models.IntegerField("Volume #", blank=True, default=None, null=True)
    issue_number = models.IntegerField("Issue #", blank=True, default=None, null=True)
    issue_name = models.CharField("Issue Name", max_length=200, blank=True)
    images = models.IntegerField("Images", default=0)
    blurb = models.TextField("Blurb", blank=True)
    slug = models.SlugField(null=False, unique=True)
    disc2_url = models.URLField("Disc 2 Webpage", blank=True)
    disc2_infinite_mac_url = models.URLField("Disc 2 ISO/DMG URL", max_length=500, blank=True)
    added = models.DateTimeField("Added", default=django.utils.timezone.now)
    def __str__(self): return self.description
    def get_absolute_url(self): return reverse("demos:source", kwargs={ "slug": self.slug })
    def get_sorted_games(self): return self.game.all().order_by('slug')
    def playable_games(self): 
        imm = self.game.exclude(infinite_mac_machine='')
        imci = self.game.exclude(infinite_mac_custom_image='')
        return imm.union(imci)
    class Meta:
        ordering = ['magazine','year', 'month', 'volume', 'issue_number', 'disc']

class Download(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, auto_created=True)
    downloads = models.IntegerField(default=0, blank=True)
    def __str__(self): return "{game} ({downloads})".format(game=self.game.game, downloads=self.downloads)

class Play(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, auto_created=True)
    plays = models.IntegerField(default=0, blank=True)
    def __str__(self): return "{game} ({plays})".format(game=self.game.game, plays=self.plays)

class Explore(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, auto_created=True)
    explores = models.IntegerField(default=0, blank=True)
    def __str__(self): return "{source} ({explores})".format(source=self.source.source, explores=self.explores)

class Website(models.Model):
    game      = models.ForeignKey(Game, on_delete=models.CASCADE)
    wikipedia = models.URLField("Wikipedia", blank=True)
    website   = models.URLField("Website", blank=True)
    mobygames = models.URLField("MobyGames", blank=True)
    steam     = models.URLField("Steam", blank=True)
    gog       = models.URLField("GOG", blank=True)
    macintosh_repository = models.URLField("Macintosh Repository", blank=True)
    macintosh_garden     = models.URLField("Macintosh Garden", blank=True)
    wayback_machine      = models.URLField("Wayback Machine", blank=True)
    github               = models.URLField("GitHub", blank=True)
    mac_source_ports     = models.URLField("Mac Source Ports", blank=True)
    def __str__(self): return self.game.game