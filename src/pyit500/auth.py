"""Module to provide the Authenticated requests"""
from hashlib import md5
from aiohttp import ClientSession, ClientResponse


class Auth:  # pylint: disable=too-few-public-methods
    """Class to make authenticated requests."""

    host = "https://sal-emea-p01-api.arrayent.com"
    auth_path = "acc/applications/SalusService/sessions"
    api_path = "zdk/services/zamapi"

    def __init__(
        self,
        websession: ClientSession,
        username: str,
        password: str,
        get_token: bool = False,
    ):
        """Initialize the auth."""
        self.websession = websession
        self.username = username
        self.passhash = md5(password.encode()).hexdigest()
        self.user_id = None
        self.security_token = None
        if get_token:
            self.refresh_token()

    def get_user_id(self) -> int:
        """Return the user ID associated with the auth session."""
        return self.user_id

    async def refresh_token(self) -> None:
        """Get user ID & security token using credentials"""
        resp = await self.websession.post(
            f"{self.host}/{self.auth_path}",
            json={"username": self.username, "password": self.passhash},
        )
        resp_values = await resp.json()
        self.user_id = resp_values["userId"]
        self.security_token = resp_values["securityToken"]

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        """Make a request."""
        if method == "post":
            auth_arg = "data"
        else:
            auth_arg = "params"

        auth_arg_value = kwargs.pop(auth_arg, {})

        if auth_arg_value is None:
            auth_arg_value = {}
        else:
            auth_arg_value = dict(auth_arg_value)

        auth_arg_value["secToken"] = self.security_token
        if "userId" not in auth_arg_value:
            auth_arg_value["userId"] = self.user_id

        kwargs[auth_arg] = auth_arg_value

        return await self.websession.request(
            method,
            f"{self.host}/{self.api_path}/{path}",
            **kwargs,
        )
