import HTMLParser
from urlparse import urlparse
import difflib

# Aleister works quite good with:
# Milliyet, Hurriyet, Haberturk, Zaman, Star

# ---FIXED--- by adding metadata parsing
# Aleister fails to get the title in Cumhuriyet
# Reason: The title is fixed <title> Cumhuriyet Portal </title>
# Title of the news is located at
# <meta property="og:title" content="Haber basligi">
#-----------------------------------------------

# ---FIXED--- by adding ':' to problematic chars
# Aleister fails to get the title in Taraf
# Reason: The title is <title> Haber: "Haber basligi" </title>
# We need to throw away the "Haber:" part
#-----------------------------------------------

# ---FIXED--- by adding '/' to problematic chars
# Aleister fails to get the title in Kanal D Haber
# Reason: The title is <title> Haber: "Haber basligi / Kanal D Haber" </title>
# We need to throw away the "/ Kanal D Haber" part
#-----------------------------------------------

# ---FIXED--- by adding metadata parsing
#Aleister fails to get the title in Sabah
# Reason: Title of the news is located at
#<meta property="og:title" content="Haber basligi"/>
#-----------------------------------------------

class Aleister(HTMLParser.HTMLParser):

    def __init__(self, *args, **kwargs):
        HTMLParser.HTMLParser.__init__(self, *args, **kwargs)
        self.in_title = False
        self.title = ''
    
    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            if ('property','og:title') in attrs:
                for metafield in attrs:
                    if metafield[0]=='content' and metafield[1]:
                        # Overwrite the title data since meta-data is more accurate
                        self.title = metafield[1].strip()
                        break

#def handle_startendtag(self, tag, attrs):
#       if tag == "meta":
#           if ('property','og:title') in attrs:
#                for metafield in attrs:
#                    if metafield[0]=='content' and metafield[1]:
                        # Overwrite the title data since meta-data is more accurate
#                        self.title = metafield[1].strip()
#                        break
                
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
        # Just remove www, not subdomains
        if(host.split('.')[0]=='www'):
            host = '.'.join(host.split('.')[1:])
        # some experimental stuff
        problematic_chars = {'-','/','\\',':'}
        for ch in problematic_chars:
            if ch in self.title:
                subs = self.title.split(ch)
                ratios = []
                for s in subs:
                    ratios.append(difflib.SequenceMatcher(a=s.strip().lower(), b=host.lower()).ratio())
                self.title = subs[ratios.index(min(ratios))].strip()
        return host
