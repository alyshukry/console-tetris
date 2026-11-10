import httpx


class ApiError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _detail(res: httpx.Response) -> str:
    if res.status_code == 422:
        return "Invalid input (username: 3-16 chars of a-z 0-9 _, password: 8+ chars)"
    try:
        detail = res.json()["detail"]
    except (ValueError, KeyError, TypeError):
        return f"Server error ({res.status_code})"
    return detail if isinstance(detail, str) else "Invalid input"


class Api:
    def __init__(self, http_base: str):
        # long timeout: a sleeping free-tier server can take a while to wake up
        self.http = httpx.Client(base_url=http_base, timeout=30, follow_redirects=True)
        self.username: str | None = None
        self.access_token: str | None = None
        self.refresh_token: str | None = None

    def _request(self, method: str, path: str, *, auth: bool = False, **kwargs):
        for attempt in range(2):
            headers = {"Authorization": f"Bearer {self.access_token}"} if auth else {}
            try:
                res = self.http.request(method, path, headers=headers, **kwargs)
            except httpx.RequestError:
                raise ApiError(0, "Can't reach the server") from None
            if res.is_success:
                return res.json()
            detail = _detail(res)
            if auth and attempt == 0 and detail == "Token expired":
                self.refresh()
                continue
            raise ApiError(res.status_code, detail)
        raise ApiError(401, "Session expired, please log in again")

    def _set_tokens(self, tokens: dict):
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

    def login(self, username: str, password: str):
        tokens = self._request(
            "POST", "/auth/login", json={"username": username, "password": password}
        )
        self._set_tokens(tokens)
        self.username = username

    def register(self, username: str, password: str):
        self._request(
            "POST", "/auth/register", json={"username": username, "password": password}
        )
        self.login(username, password)  # auto login

    def refresh(self):
        try:
            tokens = self._request(
                "POST", "/auth/refresh", json={"token": self.refresh_token}
            )
        except ApiError as e:
            if e.status == 401:
                self.access_token = self.refresh_token = None
                raise ApiError(401, "Session expired, please log in again") from None
            raise
        self._set_tokens(tokens)

    def list_rooms(self) -> list[dict]:
        return self._request("GET", "/rooms")

    def create_room(self, password: str | None):
        return self._request("POST", "/rooms", auth=True, json={"password": password})
