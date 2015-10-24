from flask import Flask, request, session, render_template
from instagram import client
from tokens import users as USERS

from scores import *
from time import sleep

app = Flask(__name__)
app.debug=True
app.secret_key = '5yJ28O3rDrJvrDz3FFlAtoCMnWxkUQuAVAUxgc'

#**** Settings ****#
CLIENT_ID = '722a889e097a45c6837cb0b4acf5eedc'
CLIENT_SECRET = '58a95fd929554034ae0285273f1575f2'

WEBSITE_URL = 'http://107.170.240.42:8080'
REDIRECT_URL = 'http://107.170.240.42:8080/redirect'

ADMIN = 'losangelesfieldoffice'
###################

auth_url = "https://api.instagram.com/oauth/authorize/?" \
           "client_id={client_id}&redirect_uri={redirect_uri}" \
           "&response_type=code"
auth_url = auth_url.format(client_id=CLIENT_ID, redirect_uri=REDIRECT_URL)

unauthenticated_api = client.InstagramAPI(client_id=CLIENT_ID,
                                          client_secret=CLIENT_SECRET,
                                          redirect_uri=REDIRECT_URL,)


@app.route('/')
def home():
    try:
        url = unauthenticated_api.get_authorize_url()
        return render_template('base.html', auth_url=url,)
    except Exception as e:
        print(e)

@app.route('/redirect')
def redirect():
    code = request.args.get('code')
    if not code:
        return 'Missing code'
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = client.InstagramAPI(access_token=access_token, client_secret=CLIENT_SECRET)
        session['access_token'] = access_token
        session['user_info'] = user_info
    except Exception as e:
        print(e)
    return "You did it! click <a href='/score/lafohunt'>to continue</a>"

@app.route('/score/<tag_name>')
def score(tag_name):
    access_token=session.get('access_token', None)
    api = client.InstagramAPI(access_token=access_token,
                       client_secret=CLIENT_SECRET)

    next_ = True
    recent_media = []
    while next_:
        recent_, next_ = api.tag_recent_media(tag_name=tag_name,
                                                   count=10)
        recent_media+=(recent_)
        sleep(1)

    scores = Scores.consume_media(recent_media)

    score_total = scores.calculate_winner()
    score_panel = ''.join([unicode(team_score) for _, team_score in scores.teams.items()])
    return ''.join((score_total, '<br>', score_panel))

if __name__ == '__main__':
    app.run(port=8080)


