from . import auth

def authenticate():
    if (auth.get_client_id() and auth.get_token()):
        return True
    else:
        return False