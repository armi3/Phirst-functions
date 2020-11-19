import os

def return_auth_url(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    client_id=os.environ.get("CLIENT_ID")
    response_type=os.environ.get("RESPONSE_TYPE")
    redirect_url=os.environ.get("REDIRECT_URL")
    scope=os.environ.get("SCOPE")
    return  {"data": {"authURL":f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type={response_type}&redirect_uri={redirect_url}&scope={scope}"}}
