import HTMLParser

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

    def handle_data(self, data):
        if self.in_title:
            self.title += data
