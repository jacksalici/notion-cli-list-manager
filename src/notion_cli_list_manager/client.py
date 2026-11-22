import requests


class NotionError(Exception):
    pass


class NotionClient:
    base_url = "https://api.notion.com/v1/"
    version = "2026-03-11"

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
        self._data_sources: dict[str, str] = {}

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

    def data_source(self, database_id: str) -> str:
        if database_id not in self._data_sources:
            sources = self.request("GET", f"databases/{database_id}")["data_sources"]
            if len(sources) != 1:
                raise NotionError(
                    f"Database {database_id} has {len(sources)} data sources, expected 1."
                )
            self._data_sources[database_id] = sources[0]["id"]
        return self._data_sources[database_id]

    def properties(self, database_id: str) -> list[str]:
        return list(
            self.request("GET", f"data_sources/{self.data_source(database_id)}")["properties"]
        )

    def query(self, database_id: str, filter: dict | None = None) -> list[dict]:
        path = f"data_sources/{self.data_source(database_id)}/query"
        pages, cursor = [], None
        while True:
            body = {"filter": filter} if filter else {}
            if cursor:
                body["start_cursor"] = cursor
            data = self.request("POST", path, json=body)
            pages += data["results"]
            if not data.get("has_more"):
                return pages
            cursor = data["next_cursor"]

    def create_page(self, database_id: str, title: str, **properties: dict) -> dict:
        parent = {"type": "data_source_id", "data_source_id": self.data_source(database_id)}
        properties = {"Name": {"title": [{"text": {"content": title}}]}, **properties}
        return self.request("POST", "pages", json={"parent": parent, "properties": properties})

    def delete_page(self, page_id: str) -> dict:
        return self.request("PATCH", f"pages/{page_id}", json={"in_trash": True})

    def markdown(self, page_id: str) -> str:
        data = self.request("GET", f"pages/{page_id}/markdown", params={"markdown_version": "v2"})
        if data["truncated"]:
            raise NotionError("Page is too large to edit as a whole.")
        return data["markdown"]

    def set_markdown(self, page_id: str, markdown: str) -> list[dict]:
        """Replace the page body; returns Notion's warnings, if any."""
        body = {
            "markdown_version": "v2",
            "type": "replace_content",
            "replace_content": {"new_str": markdown},
        }
        return self.request("PATCH", f"pages/{page_id}/markdown", json=body).get("warnings", [])
