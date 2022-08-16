from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os
import pandas as pd

app = Flask(__name__)


client_id = "LzaVkmDJ4BAPzAvnqTP5ySSE"
client_secret = "aOWNWcNywusU67r7EKvh9lilLqBZW8O098EYL7AAHAzlrIqS"
authorization_base_url = 'http://127.0.0.1:5000/oauth/authorize'
token_url = 'http://127.0.0.1:5000/oauth/token'

global state_13082022

@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    global state_13082022

    api_session = OAuth2Session(client_id)
    authorization_url, state_13082022 = api_session.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state_13082022
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    api_session = OAuth2Session(client_id, state=state_13082022)
    token = api_session.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    df = pd.read_csv('data.csv')
    serie = {}
    for i in range(len(df)):
        serie[df['data'].iloc[i]] = float(df['y'].iloc[i])
    post = {'timeseries':serie,
    'periods':24}
    api_session = OAuth2Session(client_id, token=session['oauth_token'])
    return api_session.post('http://127.0.0.1:5000/timeseries',json = post).json()


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=False,port=8000)