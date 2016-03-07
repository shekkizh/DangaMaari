import os, sys, inspect
import urllib
import webapp2
import jinja2

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"lib")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from googleapiclient.discovery import build
from optparse import OptionParser

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), extensions=['jinja2.ext.autoescape'])

# Set DEVELOPER_KEY to the "API key" value from the "Access" tab of the
# Google APIs Console http://code.google.com/apis/console#access
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyCq_AkZGuFIIgG97ibj7WZNA5F5L4VqEqI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
QUERY = "Danga Maari"


class MainHandler(webapp2.RequestHandler):
    def get(self):
        if DEVELOPER_KEY == "REPLACE_ME":
            self.response.write("""You must set up a project and get an API key to run this project.  Please visit <landing page> to do so.""")
        else:
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
            search_response = youtube.search().list(q= QUERY, part="id,snippet", maxResults=10).execute()

            videos = []

            for search_result in search_response.get("items", []):
                if search_result["id"]["kind"] == "youtube#video":
                    videos.append([search_result["id"]["videoId"],search_result["snippet"]["title"]])

            template_values = {
                'videos': videos
            }

            self.response.headers['Content-type'] = 'text/html'
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/.*', MainHandler), ], debug=True)
