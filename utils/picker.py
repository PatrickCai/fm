import random
from constants import main
from constants.main import MAX_PAST_ARTISTS, LEVELS_ORDER, MAX_PAST_TRACKS
from constants.main import MAX_PAST_EMOTION_ARTISTS, MAX_PAST_EMOTION_TRACKS
from constants.main import EMOTION_ORDER, MAX_PAST_TAGS
from models import userTrack

from utils import fredis, zeus

LIB_RATIO = 75


class FixedLengthList(object):
    def __init__(self, length, username, limit_name):
        self.length = length
        self.key_name = "%slimit:%s" % (limit_name, username)

    def append(self, item):
        if fredis.r_cli.llen(self.key_name) >= self.length:
            fredis.r_cli.lpop(self.key_name)
        fredis.r_cli.rpush(self.key_name, item)

    def exist(self, item):
        '''
        Check whether the item is in the list
        '''
        items_in_list = fredis.r_cli.lrange(self.key_name, 0, -1)
        return True if item in items_in_list else False


class EmotionPicker(object):
    def __init__(self, username, emotion, emotion_tracks):
        self.username = username
        self.emotion = emotion
        self.emotion_tracks = emotion_tracks
        self.past_artists = FixedLengthList(MAX_PAST_EMOTION_ARTISTS, username,
                                            'artists')
        self.past_tracks = FixedLengthList(MAX_PAST_EMOTION_TRACKS, username,
                                           'tracks')
        self.choice_pos = 0

    def next_track(self):
        while 1:
            random.shuffle(self.emotion_tracks)
            chosen_track = random.choice(self.emotion_tracks)
            if not self.past_artists.exist(chosen_track.artist) and \
                    not self.past_tracks.exist(chosen_track.title) and \
                    self.in_choice(chosen_track):
                break
        self.past_artists.append(chosen_track.artist)
        self.past_tracks.append(chosen_track.title)
        self.next_choice()
        return chosen_track

    def in_choice(self, chosen_track):
        lib_rec = EMOTION_ORDER[self.choice_pos]['type']
        min_value = EMOTION_ORDER[self.choice_pos]['min']
        max_value = EMOTION_ORDER[self.choice_pos]['max']
        if lib_rec == chosen_track.track_type and\
                min_value < chosen_track.emotion_value < max_value:
            return True
        else:
            return False

    def next_choice(self):
        if self.choice_pos == (len(EMOTION_ORDER) - 1):
            self.choice_pos = 0
        else:
            self.choice_pos += 1


class Picker(object):
    def __init__(self, username, emotion_range):
        self.past_artists = FixedLengthList(MAX_PAST_ARTISTS, username,
                                            "artists")
        self.past_tracks = FixedLengthList(MAX_PAST_TRACKS, username,
                                           "tracks")
        self.past_tags = FixedLengthList(MAX_PAST_TAGS, username,
                                         'tags')
        self.username = username
        self.emotion_range = emotion_range
        self.pick_pos = 0

    def _next_level_pos(self):
        '''
        Next position in the levels orders
        '''
        if self.pick_pos == (len(LEVELS_ORDER) - 1):
            self.pick_pos = 0
        else:
            self.pick_pos += 1

    def next_mix(self, track_number, lib_ratio, reverse_type, last_tag,
                 tag_value, last_emotion_value):
        '''
        Pick one song either from library or recommendation
        Depends on the LIB_RATIO
        '''
        is_lib = main.IS_LIB[lib_ratio][track_number]
        if (reverse_type == "lib" or is_lib) and not reverse_type == "rec":
            return self.next_lib(track_number, last_tag, tag_value,
                                 last_emotion_value)
        elif (reverse_type == "rec" or not is_lib) and \
                not reverse_type == "lib":
            return self.next_rec(track_number, last_tag, tag_value,
                                 last_emotion_value)

    def next_init_lib(self):
        random_track = zeus.choice(self.lib_list)
        while 1:
            random_track = random.choice(self.lib_list)
            if not self.past_artists.exist(random_track.artist) and\
                    not self.past_tracks.exist(random_track.track_uuid):
                break
        self.past_tracks.append(random_track.track_uuid)
        self.past_artists.append(random_track.artist)
        random_track.type = "lib"
        return random_track

    def next_lib(self, track_number, last_tag, tag_value, last_emotion_value):
        '''
        Choose next track from the user's own library
        '''
        user_track_uuids = userTrack.get_user_uuids(self.username, 'lib')
        emotion_tracks = userTrack.get_user_tracks_detail(
            user_track_uuids, emotion_range=self.emotion_range,
            last_tag=last_tag, tag_value=tag_value, track_number=track_number)
        random.shuffle(emotion_tracks)
        emotion_tracks, is_no_tag = self._tag_filter(emotion_tracks, last_tag)
        if track_number > 0 and not is_no_tag:
            # For instance pick the track according to the last tag and emotion
            emotion_tracks = self._ordered_tracks(
                emotion_tracks, last_emotion_value, tag_value,
                track_number)

        for random_track in emotion_tracks:
            if not self.past_artists.exist(random_track.artist) and\
                    not self.past_tracks.exist(random_track.track_uuid):
                next_track = random_track
                self._set_next_tag(next_track, is_no_tag)
                break

        else:
            # @todo(Re-choose the sample tracks from db)
            print("Fix it ")
            next_track = random.choice(emotion_tracks)

        self.past_tracks.append(next_track.track_uuid)
        self.past_artists.append(next_track.artist)
        next_track.type = "lib"
        return next_track

    def next_rec(self, track_number, last_tag, tag_value, last_emotion_value):
        '''
        Choose next track from the user's recommendation
        '''
        user_track_uuids = userTrack.get_user_uuids(self.username, 'rec')
        emotion_tracks = userTrack.get_user_tracks_detail(
            user_track_uuids, emotion_range=self.emotion_range,
            last_tag=last_tag, tag_value=tag_value, track_number=track_number)
        random.shuffle(emotion_tracks)
        emotion_tracks, is_no_tag = self._tag_filter(emotion_tracks, last_tag)
        if last_tag != "random" and not is_no_tag:
            emotion_tracks = self._ordered_tracks(
                emotion_tracks, last_emotion_value, tag_value,
                track_number)

        for rec_track in emotion_tracks:
            if not self.past_artists.exist(rec_track.artist):
                next_track = rec_track
                self._set_next_tag(next_track, is_no_tag)
                break
        else:
            next_track = random.choice(emotion_tracks)

        self.past_artists.append(next_track.artist)
        next_track.type = "rec"
        return next_track

    def _ordered_tracks(self, next_tracks, last_emotion_value, tag_value,
                        track_number):
        '''
        Order the tracks with the two factors (tag_value and emotion_value)
        '''
        for next_track in next_tracks:
            dif_value = abs(next_track.tag_value - tag_value) + \
                abs(next_track.emotion_value - last_emotion_value)
            next_track.dif_value = dif_value
        next_tracks = sorted(next_tracks, key=lambda x: x.dif_value)
        chosen_tracks = [next_track for next_track in next_tracks
                         if next_track.dif_value >=
                         main.EMOTION_MIN_DIFF[track_number]]
        print("The waiting list number %s" % (len(chosen_tracks)))
        if not chosen_tracks:
            print("Exception No min diff")
            chosen_tracks = next_tracks
        return chosen_tracks

    def _in_emo_range(self, emo_range, emotion_value):
        '''
        Return True if the emotion_value is in the emo_range
        '''
        if emo_range[0] <= emotion_value <= emo_range[1]:
            return True
        else:
            return False

    def _tag_filter(self, emotion_tracks, last_tag):
        '''
        Filter those tracks whose tags not meet the standard
        '''
        if last_tag == "random":
            return emotion_tracks
        filtered_emotion_tracks = []
        for emotion_track in emotion_tracks:
            for i in range(1, 5):
                tag = getattr(emotion_track, 'tag%s' % i)
                if tag == last_tag:
                    emotion_track.tag = tag
                    emotion_track.tag_value = getattr(emotion_track,
                                                      'tag_value%s' % i)
                    filtered_emotion_tracks.append(emotion_track)
                    break
        if not filtered_emotion_tracks:
            print("Tags all not meet the standard")
            is_no_tag = True
            return emotion_tracks, is_no_tag
        is_no_tag = False
        return filtered_emotion_tracks, is_no_tag

    def _set_next_tag(self, next_track, is_no_tag):
        '''
        Set next track's tag
        '''
        if not is_no_tag:
            self.past_tags.append(next_track.tag)
        for i in range(1, 5):
            tag = getattr(next_track, 'tag%s' % i)
            tag_value = getattr(next_track, 'tag_value%s' % i)
            if not self.past_tags.exist(tag):
                print('next tag %s' % (tag))
                next_track.last_tag = tag
                next_track.last_tag_value = tag_value
                break
        else:
            next_track.last_tag = 'random'
            next_track.last_tag_value = 100
