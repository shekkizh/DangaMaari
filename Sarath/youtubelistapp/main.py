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
    # Create a liveBroadcast resource and set its title, scheduled start time,
    # scheduled end time, and privacy status.
    def insert_broadcast(youtube):
        insert_broadcast_response = youtube.liveBroadcasts().insert(
            part="snippet,status",
            body=dict(
                snippet=dict(
                    title="New Broadcast",
                    scheduledStartTime='2016-03-24T00:00:00.000Z',
                    scheduledEndTime='2016-03-25T00:00:00.000Z'
                ),
                status=dict(
                    privacyStatus="private"
                )
            )
        ).execute()

        snippet = insert_broadcast_response["snippet"]

        print "Broadcast '%s' with title '%s' was published at '%s'." % (
            insert_broadcast_response["id"], snippet["title"], snippet["publishedAt"])
        return insert_broadcast_response["id"]

    # Create a liveStream resource and set its title, format, and ingestion type.
    # This resource describes the content that you are transmitting to YouTube.
    def insert_stream(youtube):
        insert_stream_response = youtube.liveStreams().insert(
            part="snippet,cdn",
            body=dict(
                snippet=dict(
                    title="New Stream"
                ),
                cdn=dict(
                    format="1080p",
                    ingestionType="rtmp"
                )
            )
        ).execute()

        snippet = insert_stream_response["snippet"]

        print "Stream '%s' with title '%s' was inserted." % (
            insert_stream_response["id"], snippet["title"])
        return insert_stream_response["id"]

    # Bind the broadcast to the video stream. By doing so, you link the video that
    # you will transmit to YouTube to the broadcast that the video is for.
    def bind_broadcast(youtube, broadcast_id, stream_id):
        bind_broadcast_response = youtube.liveBroadcasts().bind(
            part="id,contentDetails",
            id=broadcast_id,
            streamId=stream_id
        ).execute()

        print "Broadcast '%s' was bound to stream '%s'." % (
            bind_broadcast_response["id"],
            bind_broadcast_response["contentDetails"]["boundStreamId"])

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

            # broadcast_id = self.insert_broadcast(youtube, args)
            # stream_id = self.insert_stream(youtube, args)
            # self.bind_broadcast(youtube, broadcast_id, stream_id)

            template_values = {
                'videos': videos
            }

            self.response.headers['Content-type'] = 'text/html'
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/.*', MainHandler), ], debug=True)
