import HTMLParser
from urlparse import urlparse
import difflib

class Aleister(HTMLParser.HTMLParser):

    def __init__(self, *args, **kwargs):
        HTMLParser.HTMLParser.__init__(self, *args, **kwargs)
        self.in_title = False
        self.title = ''
        
    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
                
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            self.title = self.title.strip()
            # some experimental stuff from now on
            if '\r\n' in self.title:
                self.title = self.title[:self.title.index('\r\n')].strip()
            

    def handle_data(self, data):
        if self.in_title:
            self.title += data

    def parse_domain(self, url):
        host = urlparse(url).hostname
        if(len(host.split('.'))>2):
            host = '.'.join(host.split('.')[1:])
        # some experimental stuff
        if '-' in self.title:
            subs = self.title.split('-')
            ratios = []
            for s in subs:
                ratios.append(difflib.SequenceMatcher(a=s.strip().lower(), b=host.lower()).ratio())
            self.title = subs[ratios.index(min(ratios))].strip()
        return host
