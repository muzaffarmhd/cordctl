import keyring
import sys

import keyring.errors

SERVICE_NAME = "zuffer"
TOKEN_USERNAME = "discord_bot_token"
CLIENT_USER_NAME = "discord_client_id"

def store_token(token):
    try:
        keyring.set_password(SERVICE_NAME, TOKEN_USERNAME, token)
        print("Token configured successfully. You are logged in!", file=sys.stderr)
    except keyring.errors.KeyringError as e:
        print(f"Error storing token: {e}", file=sys.stderr)

def get_token():
    try:
        token = keyring.get_password(SERVICE_NAME, TOKEN_USERNAME)
        return token
    except keyring.errors.KeyringError as e:
        print(f"Error retrieving token: {e}", file=sys.stderr)
        return None

def delete_token():
    try:
        keyring.delete_password(SERVICE_NAME,TOKEN_USERNAME)
        return True
    except keyring.errors.PasswordDeleteError:
        # print("Token isn't configured, nothing to delete, first login.")
        return True
    except keyring.errors.KeyringError as e:
        print(f"Error deleting the token: {e}", file=sys.stderr)
        return False
    
def store_client_id(client_id):
    try:
        keyring.set_password(SERVICE_NAME, CLIENT_USER_NAME, client_id)
        print("Client configured successfully. Please run `zuffer refresh`", file=sys.stderr)
    except keyring.errors.KeyringError as e:
        print(f"Error storing token: {e}", file=sys.stderr)

def get_client_id():
    try:
        client_id = keyring.get_password(SERVICE_NAME, CLIENT_USER_NAME)
        return client_id
    except keyring.errors.KeyringError as e:
        print(f"Error retrieving token: {e}", file=sys.stderr)
        return None
def delete():
    try:
        keyring.delete_password(SERVICE_NAME,TOKEN_USERNAME)
        keyring.delete_password(SERVICE_NAME,CLIENT_USER_NAME)
        return True
    except keyring.errors.PasswordDeleteError:
        # print("Token isn't configured, nothing to delete, first login.")
        return True
    except keyring.errors.KeyringError as e:
        print(f"Error deleting the token: {e}", file=sys.stderr)
        return False
  