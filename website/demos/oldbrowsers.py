from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class DetectOldBrowser:

    user_agent_strings = (
            'OS9',
            'Classilla',
            'Cyberdog',
            'MacMosaic',
            '68K',
            'PPC',
            'PowerPC',
            'TenFourFox',
            'AquaFox',
            'Mac OS X 10.5',
            'Mac OS X 10_5',
            'Mac OS X 10.6',
            'Mac OS X 10_6',
            'Mac OS X 10.7',
            'Mac OS X 10_7',
            'BeOS',
            'cghmn-google-crawler',
        )

    def is_old_browser(self,user_agent):
        for uas in self.user_agent_strings:
            if uas in user_agent:
                return True
        return False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not 'is_old_browser' in request.session:
            request.session['is_old_browser'] = self.is_old_browser(request.headers["User-Agent"])
        if request.scheme == 'http' and not request.session['is_old_browser'] and not settings.DEBUG:
            return HttpResponsePermanentRedirect("https://" + request.get_host() + request.path )
        else:
            return self.get_response(request)