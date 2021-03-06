import os


API_KEY = "9196fd3c8cebc35c969bcd08cf69416d"
API_SECRET = "f0067afc3af73cb86a77bb50c3163784"


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MIN_TRACK_PLAYCOUNT = 3

INIT_RADIO_TYPE = 'normal'
CACHE_LIST_NUMBER = 8
LIB_RATIO = 60

TOP_RATIO = 40
RECENT_RATIO = 40
LOVED_RATIO = 20

PRE_TRACKS_NUMBER = 20

MAX_PAST_ARTISTS = 15
MAX_PAST_TRACKS = 180
MAX_PAST_EMOTION_ARTISTS = 10
MAX_PAST_EMOTION_TRACKS = 30
MAX_PAST_TAGS = 4

TITLE_BANNED = set(['REMIX', "LIVE"])

ALBUM_BANNED = ["DAYTROTTER SESSION", 'DAYTROTTER SESSIONS',
                "ITUNES SESSION", 'ITUNES SESSIONS', "LIVE",
                "DAYTROTTER STUDIO"]

SAMPLE_TRACKS_NUMBER = 800

IS_LIB = {
    20: [1, 0, 0, 0, 0],
    40: [1, 0, 1, 0, 0],
    60: [1, 1, 0, 1, 0],
    80: [1, 1, 1, 1, 0],
    100: [1, 1, 1, 1, 1],
}

LIB_ORDER = ['lib', 'lib', 'rec', 'lib', 'rec']

EMOTION_RANGE = [[start_value * 25, start_value * 25 + 25]
                 for start_value in xrange(0, 15)]


EMOTION_AREA = [[0, 100], [100, 200], [200, 300], [300, 400]]


EMOTION_MIN_DIFF = {
    1: 0,
    2: 5,
    3: 10,
    4: 15,
}

EMOTION_ADDED_VALUE = 15

EMOTION_ORDER = [
    {'type': 'lib', "min": 95, "max": 100},
    {'type': 'lib', "min": 90, "max": 100},
    {'type': 'lib', "min": 80, "max": 100},
    {'type': 'rec', "min": 95, "max": 100},
    {'type': 'lib', "min": 80, "max": 100},
    {'type': 'lib', "min": 75, "max": 100},
    {'type': 'rec', "min": 70, "max": 100},
    {'type': 'lib', "min": -20, "max": 100},
    {'type': 'rec', "min": 60, "max": 100},
    {'type': 'lib', "min": -20, "max": 100},
    {'type': 'rec', "min": 80, "max": 100},
    {'type': 'rec', "min": -20, "max": 100},
    {'type': 'lib', "min": 80, "max": 100},
    {'type': 'rec', "min": -20, "max": 100},
    {'type': 'rec', "min": -20, "max": 100},
]

MIN_ARTIST_PLAYCOUNT = 200

LEVELS_ORDER = [4, 3, 2, 4, 3, 2, 1]

STORED_TRACKS_NUMBER = 5
STORED_EMOTION_NUMBER = 15

USER_TOP_ARTISTS_NUMBER = 200

SEARCH_URL = 'http://music.163.com/api/search/get'
API_HEADERS = {"Referer": "http://music.163.com"}
API_COOKIE = {"appver": '2.0.2'}
MP3_FILE_PREFIX = 'http://m1.music.126.net/'


NEIGHBOUR_RATE_RULES = {
    "start_value": 3,
    "end_value": 7,
}
NEIGHBOUR_OVERALL_RATE_RULES = {
    "start_value": 60,
    "end_value": 100,
}

WY_ARTIST_PREFIX = 'http://music.163.com/#/artist?id='
WY_ALBUM_PREFIX = "http://music.163.com/#/album?id="
WY_SONG_PREFIX = 'http://music.163.com/#/song?id='

VALID_TAGS = ["ambient", "blues", "classic rock", "country", "dance",
              "easy listening", "emo", "folk", "gothic", "hip-hop",
              "minimal", "new wave", "noise", "piano", "post-punk",
              "post-rock", "psychedelic", "punk", "reggae", "Rnb",
              "shoegaze", "singer-songwriter", "Ska", "trip-hop",
              "Synthpop", "beautiful", "chillout", "cool", "melancholy",
              "Mellow", "sad", "romantic", "saxophone", 'Lo-fi', 'summer',
              'epic', 'calm', "electronic", "britpop", "jazz",
              "lush"]

NOT_EMOTION_TAGS = ["blues", "classic rock", "country", "dance",
                    "easy listening", "emo", "folk", "gothic", "hip-hop",
                    "minimal", "new wave", "noise", "piano", "post-punk",
                    "post-rock", "psychedelic", "punk", "reggae", "Rnb",
                    "shoegaze", "singer-songwriter", "trip-hop",
                    "Synthpop", "chillout", "melancholy",
                    "Mellow", "sad", 'Lo-fi',
                    'epic', 'calm', "electronic", "britpop", "jazz",
                    ]

TAGS_VALUE = ['1', '2']


# value to tell the track apart
MIDDLE_VALUE = 50
LOWEST_VALUE = 20

MIN_DUMMY = 1


def get_dfsid_url(song_id):
    url = r'http://music.163.com/api/song/detail/?id\
            =%s&ids=%s5B%s%s5D&csrf_token=Method=GET' % (
        song_id, '%', song_id, "%")
    return url


def emotion_range_add(emotion_range, track_number):
    '''
    According to the track number determine the final emotion range
    '''
    track_emotion = {
        0: [0, 15],
        1: [5, 20],
        2: [10, 25],
        3: [15, 25],
        4: [0, 25],
    }
    add_emotion = track_emotion[track_number]
    added_start_value, added_end_value = add_emotion
    emo_range = []
    emo_range.append(emotion_range[0] + added_start_value)
    emo_range.append(emotion_range[0] + added_end_value)
    return emo_range
