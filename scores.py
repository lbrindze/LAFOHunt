from geopy.distance import vincenty

master_locations = [(34.048783 , -118.233691),
(34.047164 , -118.227509),
(34.047634 , -118.225940),
(34.047363 , -118.226513),
(34.047984 , -118.230105),
(34.046390 , -118.237669),
(34.048285 , -118.232642),
(34.045752 , -118.236579),
(34.044888 , -118.234597),
(34.048764 , -118.237098),
(34.047428 , -118.219950),
(34.046264 , -118.216037),
(34.047611 , -118.219277),
(34.047180 , -118.218451),
(34.047015 , -118.218069),
(34.053085 , -118.245914),
(34.055133 , -118.245109),
(34.057983 , -118.249187),
(34.054165 , -118.250653),
(34.052182 , -118.241069),
(34.048841 , -118.238361),
(34.051277 , -118.238999),
(34.045096 , -118.238816),
(34.049249 , -118.240172),
(34.050064 , -118.241936),
(33.981275219, -118.458290163),]

class ScoreKeeper(object):
    """
    This object is in charge of tallying up and recording an individual's score.
    Instantiate this object with a list of locations that the user has visited and a master list of locations.
    Activate the score card by calling self.tally_up()
    Add more locations by calling self.add_locations()
    Dependency: geopy 1.11.0
        pip install geopy
    """

    def __init__(self, user_locations, master_locations, threshold):
        self.user_locations = user_locations
        self.master_locations = { loc: False for loc in master_locations}
        self.threshold = threshold

    def tally_up(self):
        # Push each location through verification function and toggle switches based on return boolean
        # Calculate distance between location[i] and master_locations[i]. If distance is less than "x" then toggle switches
        for loc in self.user_locations:
            for k in self.master_locations:
                self.master_locations[k] = ScoreKeeper.is_within_x_feet(loc, k, self.threshold)
        return self.master_locations

    @staticmethod
    def is_within_x_feet(loc1, loc2,threshold):
        return vincenty(loc1, loc2).ft <= threshold

    def add_locations(self, locations):
        for location in locations:
            self.locations.append(location)

class Scores(object):
    teams = {}

    def __init__(self, *user_scores):
        for user_score in user_scores:
            self.add_team(user_score)

    @classmethod
    def consume_media(cls, recent_media):
        scores = cls()
        for media in recent_media:
            user_score = scores.teams.get(media.user.username, None)

            if not user_score:
                user_score = UserScore(media)
                scores.add_team(user_score)
            user_score.add_media(media)

        return scores


    def add_team(self, user_score):
        if not user_score.user in self.teams:
            self.teams[user_score.user.username] = user_score

        return self.teams

    def calculate_winner(self):
        return [(k, x.score) for k, x in self.teams]

class UserScore(object):
    score = 0
    locations_visited = []

    def __init__(self, media):

        self.user = getattr(media, 'user', None)
        if self.user is not None:
            self.posts = []
            self.add_media(media)

    def calculate_score(self):
        locations = [(x.location.point.latitude,\
                     x.location.point.longitude)\
                             for x in self.posts if hasattr(x, 'location')]
        score_keeper = ScoreKeeper(locations, master_locations, 500.0)
        location_tally = score_keeper.tally_up().items()
        self.locations_visited = [x[0] for x in location_tally if x[1]]

        self.score = len(self.locations_visited)
        return self.score

    def add_media(self, media):
        if media not in self.posts:
            self.posts.append(media)
            self.calculate_score()

    def __repr__(self):
        return ''.join(('<UserScore ', self.user.username, str(self.score), '>'))

    def __unicode__(self):
        self.calculate_score()
        out = ''
        out += ' '.join((self.user.username, str(self.score)))
        out += '<br>'+'='*5
        out += '<br>'

        for post in self.posts:
            out+= "<a href='{}'> image</a><br>".format(post.images.get('standard_resolution').url)
            out+= "<img src='{}'></img><br>".format(post.images.get('thumbnail').url)
            try:
                out += ''.join(("LAT: ", str(post.location.point.latitude),'</br>',
                                "LNG: ", str(post.location.point.longitude),  '<br>'))
            except Exception as e:
                out += ''.join(("NO LOCATION<br>"))
            out+= '-' * 10
            out+='<br>'

        return out
