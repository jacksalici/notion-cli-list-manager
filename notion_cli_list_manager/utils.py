from pathlib import Path
import requests
import toml
import typer

class TomlHelper:
    """Helper class for TOML file operations."""
    
    SCRIPT_LOCATION = Path(__file__).absolute().parent
    CONFIG_FILE = SCRIPT_LOCATION / "config.toml"
    PAGES_FILE = SCRIPT_LOCATION / "pages.toml"

    @staticmethod
    def get_dict(file_path, verbose=False):
        """Load a TOML file into a dictionary."""
        try:
            with open(file_path, "r+") as file:
                return toml.load(file)
        except FileNotFoundError:
            if verbose:
                typer.secho("File not found.", err=True, fg='yellow')
        except toml.TomlDecodeError:
            typer.secho("File encoding error.", err=True, fg='yellow')
        
        return {}
    
    @staticmethod
    def set_dict(data_dict, file_path):
        """Save a dictionary to a TOML file."""
        try:
            with open(file_path, "w") as file:
                file.write(toml.dumps(data_dict))
                return True
        except Exception as e:
            typer.secho(f"Error writing to file: {e}", err=True, fg='yellow')
            return False
    
    @classmethod
    def get_db_id(cls, database):
        """Get database ID from config."""
        try:
            config = cls.get_dict(cls.CONFIG_FILE)
            return str(config.get("databases", {}).get(database, {}).get("id", ""))
        except Exception:
            return ""

    @classmethod
    def get_db_keys(cls):
        """Get all database keys from config."""
        try:
            return cls.get_dict(cls.CONFIG_FILE).get("databases", {}).keys()
        except Exception:
            return []

    @classmethod
    def get_db_prop(cls, database):
        """Get properties for a specific database."""
        try:
            return cls.get_dict(cls.CONFIG_FILE).get("databases", {}).get(database, {}).get("properties", [])
        except Exception:
            return []


class NotionAPI:
    """Helper class for Notion API operations."""
    
    API_BASE_URL = "https://api.notion.com/v1/"
    API_VERSION = "2021-08-16"
    
    def __init__(self):
        self.token = self.get_token()
        self.headers = self.create_headers()
    
    @staticmethod
    def get_token():
        """Get the Notion API token from config."""
        config = TomlHelper.get_dict(TomlHelper.CONFIG_FILE)
        return str(config.get("token", ""))
    
    def create_headers(self):
        """Create headers for Notion API requests."""
        return {
            "Authorization": self.token,
            "Notion-Version": self.API_VERSION,
            "Content-Type": "application/json"
        }
    
    def make_request(self, method, endpoint, data=""):
        """Make a request to the Notion API."""
        url = f"{self.API_BASE_URL}{endpoint}"
        
        try:
            response = method(url, headers=self.headers, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                typer.secho(f"API error: {response.status_code} - {response.text}", err=True, fg='yellow')
                return {"object": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            typer.secho(f"Request error: {e}", err=True, fg='yellow')
            return {"object": "error", "message": str(e)}
    
    def get_database(self, database_id):
        """Get database details."""
        return self.make_request(requests.get, f"databases/{database_id}")
    
    def get_db_props(self, database_id):
        """Get database properties."""
        response = self.get_database(database_id)
        
        try:
            properties = response.get("properties", {})
            if isinstance(properties, dict):
                return properties.keys()
            return []
        except Exception:
            return []
    
    def new_page(self, title, database_id, custom_data=None):
        """Create a new page in a database."""
        if custom_data:
            data = custom_data
        else:
            data = f'{{"parent":{{"database_id":"{database_id}"}},"properties":{{"Name":{{"title":[{{"text":{{"content":"{title}"}}}}]}}}}}'
        
        return self.make_request(requests.post, "pages", data)
    
    def get_pages(self, database_id):
        """Query pages in a database."""
        return self.make_request(requests.post, f"databases/{database_id}/query", "")
    
    def remove_page(self, page_id):
        """Delete a page."""
        return self.make_request(requests.delete, f"blocks/{page_id}")