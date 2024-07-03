"""ensure access to box folder"""

import yaml
from boxsdk import Client, OAuth2

###################################################
CLIENT_ID = "le8w82s9irj8pv6kv5ze61j7fc28tggo"
CLIENT_SECRET = "7KaS61xBX6QYjBX5p1thNdUnFiQv6CHw"
REDIRECT_URI = "http://localhost:5000/oauth/callback"
FOLDER_ID = "200099021915"
###################################################


def save_tokens(access_token: str, refresh_token: str):
    """Save tokens into a token.yaml"""
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    with open("box/tokens.yaml", "w", encoding="utf-8") as f:
        yaml.dump(tokens, f)


def load_tokens():
    """Load tokens from tokens.yaml"""
    try:
        with open("box/tokens.yaml", "r", encoding="utf-8") as f:
            tokens = yaml.safe_load(f)
        return tokens["access_token"], tokens["refresh_token"]
    except FileNotFoundError:
        return None, None


def get_box_client() -> Client:
    """Get box client"""
    oauth2 = OAuth2(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        store_tokens=save_tokens,
        access_token=load_tokens()[0],
        refresh_token=load_tokens()[1],
    )

    access_token, refresh_token = load_tokens()

    if not access_token or not refresh_token:
        auth_url, _ = oauth2.get_authorization_url(REDIRECT_URI)
        print(f"Go to the following URL to authenticate: {auth_url}")
        authorization_code = input("Enter the authorization code provided in the URL: ")
        access_token, refresh_token = oauth2.authenticate(authorization_code)
        save_tokens(access_token, refresh_token)

    client = Client(oauth2)

    return client


def get_box_folder():
    """Get box folder to proteomics"""
    client = get_box_client()
    return client.folder(folder_id=FOLDER_ID).get()


if __name__ == "__main__":
    get_box_client()
