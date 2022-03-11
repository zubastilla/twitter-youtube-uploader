# %%
import tweepy
import urllib.request
import re
import datetime
import os
import pickle
import glob2

from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# %%
####################################################################### YOU HAVE TO FILL THIS OUT / CHECK ##################################################################################################################################
############################################################################################################################################################################################################################################
############################################################################################################################################################################################################################################
# TWITTER CREDENTIALS
consumer_key = ''
consumer_secret = ''
callback_uri = 'oob' # twitter does not require a callback uri
access_token = ''
access_secret = ''

# YOUTUBE CREDENTIALS 
CLIENT_SECRET_FILE = 'youtube_client_secrets.json' # Add your credentials to the JSON attached
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

credentials = None

# GENERATING/RETRIEVING TOKEN WITH PICKLE
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:  # rb - read bytes
        credentials = pickle.load(token)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print("Refreshing Access Token...")
        credentials.refresh(Request())
    else:
        print("Fetching New Tokens...")
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES
        )
        flow.run_local_server(
            port=8080, prompt='consent', authorization_prompt_message=''
        )
        credentials = flow.credentials

        with open('token.pickle', 'wb') as f: # wb - write bytes
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

# BUILDING TWITTER API WITH TWEEPY
auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
me = api.verify_credentials()

# BUILDING YOUTUBE API
youtube = build(API_NAME, API_VERSION, credentials=credentials)

# Twitter Variables To Set
TWITTER_HANDLE = "WBHomeEnt" # this is the page where you'll downloading videos
NUMBER_OF_TWEETS = 20 # this is the number of posts you want to screen through
EXCLUDE_REPLIES = True # this is so you get more videos, because people rarely reply with their own media

# Youtube Variables To Set
VIDEO_THUMBNAIL_OUTPUT_PATH = "C:\\Users\\YOUR_USERNAME\\Documents\\twitter-youtube-uploader\\output"
VIDEO_FORMAT = ".mp4" # if you'd like the video to be saved in a different format, modify that
IMAGE_FORMAT = ".png" # if you'd like the image to be saved in a different format, modify that
YOUTUBE_VIDEO_CATEGORY = 25 # please see the attached "youtube api video category id list.txt" file for reference

# ONLY USE IF YOU UPLOAD VIDEOS ONE BY ONE
VIDEO_TITLE = "" # if left empty, the title of the file aka the tweet will be used
VIDEO_DESCRIPTION = "" # if left empty, the title of the file aka the tweet will be used
TAGS = [] # if left empty, the words in the title aka the tweet will be used (except for common words)

# Words that are Being Filtered out from Tags when Using Default Video Title as Tags
COMMON_WORDS = ['is','are','or', 'to','a','the','this','that','these','those','them','do','does', 'in', 'and', 'on', 'off', 'with']

# Set Time or Leave Empty to Have the Current Time Used for the Upload (When not Scheduling)
UPLOAD_DATE_TIME = {'year': 0, 'month': 0, 'day': 0, 'hour': 0, 'minute': 0, 'second': 0} #  if left empty, the current time will be used

# Youtube Video Settings
PRIVACY_STATUS = 'private' # set to private by default, change to "public" if you have the necessary API priviledges
SELF_DECLARED_FOR_KIDS = False # you have to declare if the video's been made for kids here
NOTIFY_SUBSCRIBERS = False # you can notify your subscribers

############################################################################################################################################################################################################################################
############################################################################################################################################################################################################################################
############################################################################################################################################################################################################################################

# %%
# GET USERS TIMELINE
user = api.get_user(screen_name=f'{TWITTER_HANDLE}')
# user_timeline = user.timeline(count=5, exclude_replies=True) # up to 200 tweets
user_timeline = api.user_timeline(
    screen_name=f'{TWITTER_HANDLE}', count=NUMBER_OF_TWEETS, exclude_replies={EXCLUDE_REPLIES})
for i, status in enumerate(user_timeline):
    user_timeline_status_obj = user_timeline[i]
    status_obj_id = user_timeline_status_obj.id
    status_obj_screen_name = user_timeline_status_obj.user.screen_name
    status_obj_url = f'https://twitter.com/{status_obj_screen_name}/status/{status_obj_id}'
    print(i)
    print(status_obj_screen_name)
    print(status_obj_url)
    status_obj = api.get_status(status_obj_id, tweet_mode='extended')
    try:
        status_entities = status_obj.extended_entities
        status_media = status_entities['media']
        try:
            if status_media[0]['video_info']:
                status_video_info = status_media[0]['video_info']
                status_video_variants = status_video_info['variants']
                image_url = status_media[0]['media_url_https']

                video_url = None
                bitrate = 0
                for variant in status_video_variants:
                    try:
                        variant_bitrate = variant['bitrate']
                        # print(variant_bitrate)
                        if variant_bitrate > bitrate:
                            bitrate = variant_bitrate
                            video_url = variant['url']
                    except KeyError as error:
                        print(f'The following attribute is missing: {error}')
                # print("the hightest bitrate is", bitrate)
                # print("the url with highest bitrate video is", video_url)

                def deEmojify(text):
                    regrex_pattern = re.compile(pattern="["
                                                    u"\U0001F600-\U0001F64F"  # emoticons
                                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                                    # flags (iOS)
                                                    u"\U0001F1E0-\U0001F1FF"
                                                    "]+", flags=re.UNICODE)
                    return regrex_pattern.sub(r'', text)

                tweet_text = status_obj.full_text
                tweet_text = re.sub(
                    r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", tweet_text)
                if len(tweet_text) > 158:
                    # print("Tweet length's is more than 158 characters")
                    tweet_text = tweet_text[0:157]
                tweet_text = str(tweet_text.rstrip('*\n*').splitlines()[0])
                tweet_text = re.sub("\n", "", tweet_text)
                tweet_text = re.sub(r"[\"/:<>`|?]", "", tweet_text)
                tweet_text = tweet_text.replace('&amp;', '&')
                tweet_text = tweet_text.rstrip(' ')
                tweet_text = deEmojify(tweet_text)
                print(tweet_text)
                print("Video and Image Processing...")
                try:
                    output_path = f"{VIDEO_THUMBNAIL_OUTPUT_PATH}"
                    file_path = f"{output_path}\\{tweet_text}"
                    print(tweet_text)
                    # print(f'THIS IS FILE PATH: {file_path}\\{tweet_text}{VIDEO_FORMAT}')

                    if not os.path.isdir(output_path):
                        os.mkdir(output_path)
                    if not os.path.isdir(file_path):
                        os.mkdir(file_path)
                    video = urllib.request.urlretrieve(
                        video_url, f'{file_path}\\{tweet_text}{VIDEO_FORMAT}')
                    image = urllib.request.urlretrieve(
                        image_url, f'{file_path}\\{tweet_text}{IMAGE_FORMAT}')
                    print(tweet_text)
                    print(video_url)
                    print(image_url)
                    print("Video and Image Saved...")
                except OSError as error:
                    print(error)
        except KeyError as error:
            print('This is a KeyError,', error)
    except AttributeError as error:
        print('This is an AttributeError,', error)


# %%
media_folders = glob2.glob(f'{output_path}\\*')

for folder in media_folders:
    media_list = glob2.glob(f'{folder}\\*')
    for media in media_list:
        # print(media_list)
        # print()
        # print('MEDIA: ', media)
        media = media.rsplit('\\', 1)[-1]
        if media.endswith(VIDEO_FORMAT.lower()) or media.endswith(VIDEO_FORMAT.upper()):
            video = media
            video_path = f'{folder}\\{video}'
            if VIDEO_TITLE == "":
                VIDEO_TITLE = video.removesuffix('.mp4')
                VIDEO_DESCRIPTION = VIDEO_TITLE
                if len(VIDEO_TITLE) > 100:
                    VIDEO_TITLE = VIDEO_TITLE[:100]
                if len(VIDEO_DESCRIPTION) > 5000:
                    VIDEO_DESCRIPTION = VIDEO_DESCRIPTION[:5000]
            # print('THIS IS VIDEO', video) 
        if media.endswith(IMAGE_FORMAT.lower()) or media.endswith(IMAGE_FORMAT.upper()):
            thumbnail = media
            thumbnail_path = f'{folder}\\{thumbnail}'
            # print("THIS IS THUMBNAIL", thumbnail)
        if TAGS == []:
            TAGS = re.sub("[^\w]", " ",  VIDEO_TITLE).split()
            # print(VIDEO_TITLE)
            remove_common_words = COMMON_WORDS
            TAGS = [e[:500] for e in TAGS if e not in remove_common_words]
            TAGS
            # print(TAGS)
    year = UPLOAD_DATE_TIME['year']
    month = UPLOAD_DATE_TIME['month']
    day = UPLOAD_DATE_TIME['day']
    hour = UPLOAD_DATE_TIME['hour']
    minute = UPLOAD_DATE_TIME['minute']
    second = UPLOAD_DATE_TIME['second']
    if year and month != 0:
        upload_date_time = datetime.datetime(year, month, day, hour, minute, second).isoformat() + '.000Z'
    else:
        upload_date_time = datetime.datetime.now().replace(microsecond=0).isoformat() + '.000Z'
    # print('this is title ->',VIDEO_TITLE)
    request_body = {
        'snippet': {
            'title': VIDEO_TITLE,
            'description': VIDEO_DESCRIPTION,
            'tags': TAGS,
            'categoryId': YOUTUBE_VIDEO_CATEGORY
        },
        'status': {
            'privacyStatus': PRIVACY_STATUS,
            'publishAt': upload_date_time,
            'selfDeclaredForKids': SELF_DECLARED_FOR_KIDS
        },
        'notifySubscribers': NOTIFY_SUBSCRIBERS
    }
    mediaFile = MediaFileUpload(video_path)

    response_upload = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=mediaFile
    ).execute()

    youtube.thumbnails().set(
        videoId=response_upload.get('id'),
        media_body=MediaFileUpload(thumbnail_path)
    ).execute()
    print("vicategoryId:", YOUTUBE_VIDEO_CATEGORY)
    print("title:", VIDEO_TITLE)
    print("description:", VIDEO_DESCRIPTION)
    print("tags:", TAGS)
    print()
    print(upload_date_time)
    print('LENGTH:',len(VIDEO_TITLE))

    VIDEO_TITLE = ""
    VIDEO_DESCRIPTION = ""
    TAGS = []
    


# %%



