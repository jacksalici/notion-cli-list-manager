import requests


class NotionError(Exception):
    pass


class NotionClient:
    base_url = "https://api.notion.com/v1/"
    version = "2021-08-16"

    def __init__(self, token: str, session: requests.Session | None = None):
        if not token:
            raise NotionError("No token configured: run `list set --token TOKEN`.")
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": token if token.startswith("Bearer ") else f"Bearer {token}",
                "Notion-Version": self.version,
            }
        )

    def request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = self.session.request(method, self.base_url + path, timeout=30, **kwargs)
        except requests.RequestException as e:
            raise NotionError(str(e)) from e
        if not response.ok:
            try:
                message = response.json()["message"]
            except (ValueError, KeyError):
                message = response.text
            raise NotionError(f"HTTP {response.status_code}: {message}")
        return response.json()

    def properties(self, database_id: str) -> list[str]:
        return list(self.request("GET", f"databases/{database_id}")["properties"])

    def query(self, database_id: str) -> list[dict]:
        pages, cursor = [], None
        while True:
            body = {"start_cursor": cursor} if cursor else {}
            data = self.request("POST", f"databases/{database_id}/query", json=body)
            pages += data["results"]
            if not data.get("has_more"):
                return pages
            cursor = data["next_cursor"]

    def create_page(self, database_id: str, title: str, **properties: dict) -> dict:
        properties = {"Name": {"title": [{"text": {"content": title}}]}, **properties}
        body = {"parent": {"database_id": database_id}, "properties": properties}
        return self.request("POST", "pages", json=body)

    def delete_page(self, page_id: str) -> dict:
        return self.request("DELETE", f"blocks/{page_id}")
