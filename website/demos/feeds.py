from django.contrib.syndication.views import Feed
from django.templatetags.static import static
from .models import Game, Source
from .templatetags.markdown_extras import markdown
from django.template.defaultfilters import striptags

class LatestEntriesFeed(Feed):
    title = "Classic Macintosh Game Demos"
    link  = "/"
    description = "Newly added Classic Macintosh game demos and Mac magazine cover CDs from the mid-1990s and early 2000s."

    def feed_url(self):
        return "https://classicmacdemos.com/rss/"

    def items(self): 
        games = list(Game.objects.order_by("-added")[:10])
        discs = list(Source.objects.order_by("-added")[:10])
        items = games + discs
        sorted_items = sorted(items, key=lambda x: x.added)
        sorted_items.reverse()
        return sorted_items

    def item_title(self, item): 
        if isinstance(item, Game):
            return item.game
        elif isinstance(item, Source):
            return item.description

    def item_enclosure_url(self,item):
        if isinstance(item, Game):
            if item.screens > 0:
                return 'https:' + static(f"demos/%s/screen-1.png" % item.slug)
            else:
                return 'https:' + static(f"demos/%s/icon.png" % item.slug)
        elif isinstance(item, Source):
            if item.images > 0:
                return 'https:' + static(f"discs/%s/image-1.png" % item.slug)
            else:
                return 'https:' + static("icons/cd-medium.png")

    def item_enclosure_mime_type(self, game): 
        return "image/png"
    
    def item_enclosure_length(self):
        return 1

    def item_pubdate(self, item): 
        return item.added 

    def item_description(self, item):
        description = ''
        months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Holiday"]
        if (item.blurb):
            if isinstance(item, Source) and item.month:
                description += f"released %s %s | %s" % (months[item.month], item.year, striptags(markdown(item.blurb)) ) 
            else:
                description += f"released %s | %s" % (item.year, striptags(markdown(item.blurb)))
        else:
            if isinstance(item, Source) and item.month:
                description += f"released %s %s" % (months[item.month], item.year)
            else:
                description += f"released %s" % item.year
        description += " <img src=\"{}\">".format(self.item_enclosure_url(item))
        return description
    
class LatestEntriesWithImagesFeed(Feed):
    title = "Classic Macintosh Game Demos"
    link  = "/"
    description = "Newly added Classic Macintosh game demos and Mac magazine cover CDs from the mid-1990s and early 2000s."

    def feed_url(self):
        return "https://classicmacdemos.com/rss/"

    def items(self): 
        games = list(Game.objects.order_by("-added")[:10])
        discs = list(Source.objects.filter(images__gt = 0).order_by("-added")[:10] )
        items = games + discs
        sorted_items = sorted(items, key=lambda x: x.added)
        sorted_items.reverse()
        return sorted_items

    def item_title(self, item): 
        if isinstance(item, Game):
            return item.game
        elif isinstance(item, Source):
            return item.description

    def item_enclosure_url(self,item):
        if isinstance(item, Game):
            if item.screens > 0:
                return 'https:' + static(f"demos/%s/screen-1.png" % item.slug)
            else:
                return 'https:' + static(f"demos/%s/icon.png" % item.slug)
        elif isinstance(item, Source):
            return 'https:' + static(f"discs/%s/image-1.png" % item.slug)

    def item_enclosure_mime_type(self, game): 
        return "image/png"
    
    def item_enclosure_length(self):
        return 1

    def item_pubdate(self, item): 
        return item.added 

    def item_description(self, item):
        description = ''
        months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Holiday"]
        if (item.blurb):
            if isinstance(item, Source) and item.month:
                description += f"released %s %s | %s" % (months[item.month], item.year, striptags(markdown(item.blurb)))
            else:
                description += f"released %s | %s" % (item.year, striptags(markdown(item.blurb)))
        else:
            if isinstance(item, Source) and item.month:
                description += f"released %s %s" % (months[item.month], item.year)
            else:
                description += f"released %s" % item.year
        description += " <img src=\"{}\">".format(self.item_enclosure_url(item))
        return description