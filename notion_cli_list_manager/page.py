from os import get_terminal_size
import time
import typer
from prettytable import PrettyTable
from .utils import TomlHelper, NotionAPI


class NotionPage:
    """Class to handle Notion page operations."""
    
    def __init__(self):
        self.api = NotionAPI()
    
    def add(self, title, database):
        """Add a new page to the database."""
        database_id = TomlHelper.get_db_id(database)
        if not database_id:
            typer.secho(f"Database '{database}' not found.", err=True, fg='yellow')
            return
            
        return self.api.new_page(title, database_id)

    def all_by_all(self):
        """Display pages from all databases."""
        index = 0
        table = PrettyTable()
        table.max_table_width = round(get_terminal_size().columns * 0.8)
        table.field_names = ["Index", "Name"]
        table.align["Name"] = "l"
        pages_dict = {}
        
        for key in TomlHelper.get_db_keys():
            index, table, pages_dict = self._query_database(key, index, table, pages_dict)
        
        typer.echo(table)
        TomlHelper.set_dict(pages_dict, TomlHelper.PAGES_FILE)

    def all(self, database):
        """Display pages from a specific database."""
        properties_list = ["Index"] + TomlHelper.get_db_prop(database)
        if len(properties_list) == 1:
            properties_list.append("Name")
        
        table = PrettyTable()
        table.max_table_width = round(get_terminal_size().columns * 0.95)
        table.field_names = properties_list
        table.align = "l"

        _, table, pages_dict = self._query_database(database, table=table, properties_list=properties_list)
        
        typer.echo(table)
        TomlHelper.set_dict(pages_dict, TomlHelper.PAGES_FILE)

    def _query_database(self, database, index=0, table=None, pages_dict=None, properties_list=None):
        """Query and process pages from a database."""
        if table is None:
            table = PrettyTable()
            table.field_names = ["Index", "Name"]
            table.align["Name"] = "l"
        
        if pages_dict is None:
            pages_dict = {}
            
        if properties_list is None:
            properties_list = ["Index", "Name"]
        
        database_id = TomlHelper.get_db_id(database)
        if not database_id:
            return index, table, pages_dict
            
        response = self.api.get_pages(database_id)

        if not isinstance(response, dict) or response.get("object") != "list":
            if isinstance(response, dict) and response.get("object") == "error":
                typer.echo(f"Error: {response.get('message', 'Unknown error')}")
            return index, table, pages_dict

        for page in response.get("results", []):
            row_data = self._extract_property_values(page, properties_list, index)
            table.add_row(row_data.values())
            pages_dict[str(index)] = page
            index += 1

        return index, table, pages_dict

    def _extract_property_values(self, page, properties_list, index):
        """Extract property values from a page."""
        properties = page.get("properties", {})
        row = {p: "" for p in properties_list}
        row["Index"] = index
        
        property_handlers = {
            "title": self._handle_title_property,
            "rich_text": self._handle_rich_text_property,
            "select": self._handle_select_property,
            "multi_select": self._handle_multi_select_property,
            "created_time": self._handle_simple_property,
            "number": self._handle_simple_property,
            "url": self._handle_simple_property,
            "last_edited_time": self._handle_simple_property,
            "checkbox": self._handle_checkbox_property,
            "phone_number": self._handle_simple_property,
            "email": self._handle_simple_property,
            "formula": self._handle_formula_property,
            "created_by": self._handle_person_property,
            "last_edited_by": self._handle_person_property,
            "date": self._handle_date_property,
            "people": self._handle_people_property,
            "files": self._handle_files_property
        }
        
        for property_name, property_data in properties.items():
            if property_name in row:
                property_type = property_data.get("type", "")
                if property_type in property_handlers:
                    row[property_name] = property_handlers[property_type](property_data, property_type)
        
        return row

    def _handle_title_property(self, property_data, property_type):
        path = property_data.get(property_type, [])
        if path and len(path) > 0:
            return path[0].get("text", {}).get("content", "")
        return ""

    def _handle_rich_text_property(self, property_data, property_type):
        path = property_data.get(property_type, [])
        return "".join(p.get("plain_text", "") for p in path)

    def _handle_select_property(self, property_data, property_type):
        path = property_data.get(property_type)
        if path:
            return path.get("name", "")
        return ""

    def _handle_multi_select_property(self, property_data, property_type):
        path = property_data.get(property_type, [])
        return " ".join(p.get("name", "") for p in path)

    def _handle_simple_property(self, property_data, property_type):
        value = property_data.get(property_type)
        return str(value) if value is not None else ""

    def _handle_checkbox_property(self, property_data, property_type):
        value = property_data.get(property_type)
        return "[x]" if value is True else "[ ]"

    def _handle_formula_property(self, property_data, property_type):
        path = property_data.get(property_type)
        if path:
            return path.get("string", "")
        return ""

    def _handle_person_property(self, property_data, property_type):
        path = property_data.get(property_type)
        if path:
            return path.get("name", "")
        return ""

    def _handle_date_property(self, property_data, property_type):
        path = property_data.get(property_type)
        if not path:
            return ""
            
        result = ""
        start = path.get("start")
        end = path.get("end")
        
        if start:
            result += str(start)
            if end:
                result += " -> "
        if end:
            result += str(end)
            
        return result

    def _handle_people_property(self, property_data, property_type):
        path = property_data.get(property_type, [])
        return " ".join(p.get("name", "") for p in path)

    def _handle_files_property(self, property_data, property_type):
        path = property_data.get(property_type, [])
        return " ".join(p.get("name", "") for p in path)

    def remove(self, list_of_indexes):
        """Remove pages by their indexes."""
        pages_dict = TomlHelper.get_dict(TomlHelper.PAGES_FILE)
        for index in list_of_indexes:
            page = pages_dict.get(str(index))
            if isinstance(page, dict) and "id" in page:
                self.api.remove_page(page.get("id"))
                typer.echo(f"Removed page with index {index}")

    def set_token(self, token):
        """Set the Notion API token."""
        config = TomlHelper.get_dict(TomlHelper.CONFIG_FILE)
        config["token"] = token
        if TomlHelper.set_dict(config, TomlHelper.CONFIG_FILE):
            typer.echo("Token set successfully")
        else:
            typer.secho("Failed to set token", err=True, fg='yellow')

    def set_database(self, key, database_id):
        """Add a database to the config."""
        config = TomlHelper.get_dict(TomlHelper.CONFIG_FILE)
        
        if "databases" not in config:
            config["databases"] = {}
        
        config["databases"][key] = {"id": database_id}
        
        if not TomlHelper.set_dict(config, TomlHelper.CONFIG_FILE):
            typer.secho("Failed to save database configuration", err=True, fg='yellow')
            return []
        
        properties = self.api.get_db_props(database_id)
        return list(properties)

    def generate_year_pages(self, title, database, year):
        """Generate pages for each day of the year."""
        database_id = TomlHelper.get_db_id(database)
        if not database_id:
            typer.secho(f"Database '{database}' not found.", err=True, fg='yellow')
            return
            
        months_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Check for leap year
        if int(year) % 4 == 0 and (int(year) % 100 != 0 or int(year) % 400 == 0):
            months_lengths[1] = 29
            
        total_days = sum(months_lengths)
        with typer.progressbar(length=total_days, label="Generating pages") as progress:
            for month in range(1, 13):
                for day in range(1, months_lengths[month-1] + 1):
                    date = f"{year}-{month:02d}-{day:02d}"
                    page_title = date if title == "d4t35" else title
                    
                    data = self.api.build_page_payload(
                        page_title, database_id,
                        extra_properties={"Date": {"date": {"start": date}}},
                    )

                    self.api.new_page(page_title, database_id, data)
                    progress.update(1)
                    time.sleep(0.5)  # Rate limiting to avoid API limits

    def show_databases(self):
        """Display all databases in the config."""
        db_list = TomlHelper.get_db_keys()
        if not db_list:
            typer.echo("No databases configured.")
            return
            
        table = PrettyTable()
        table.field_names = ["Label"]
        for label in db_list:
            table.add_row([label])
        typer.echo(table)

    def rm_database(self, label):
        """Remove a database from the config."""
        config = TomlHelper.get_dict(TomlHelper.CONFIG_FILE)
        if "databases" not in config or label not in config["databases"]:
            typer.secho(f"Database '{label}' not found.", err=True, fg='yellow')
            return
            
        config["databases"].pop(label)
        if TomlHelper.set_dict(config, TomlHelper.CONFIG_FILE):
            typer.echo(f"Database '{label}' removed from configuration")
        else:
            typer.secho("Failed to update configuration", err=True, fg='yellow')

    def get_properties(self, label):
        """Get properties for a database."""
        database_id = TomlHelper.get_db_id(label)
        if not database_id:
            typer.secho(f"Database '{label}' not found.", err=True, fg='yellow')
            return []
            
        return list(self.api.get_db_props(database_id))
    
    def show_properties(self, properties):
        """Display properties in a table."""
        table = PrettyTable()
        table.field_names = [i for i in range(0, len(properties))]
        table.add_row(properties)
        return table
    
    def set_properties(self, label, properties):
        """Set properties for a database in the config."""
        config = TomlHelper.get_dict(TomlHelper.CONFIG_FILE)
        
        if "databases" not in config or label not in config["databases"]:
            typer.secho(f"Database '{label}' not found.", err=True, fg='yellow')
            return
            
        config["databases"][label]["properties"] = properties
        
        if TomlHelper.set_dict(config, TomlHelper.CONFIG_FILE):
            typer.echo(f"Properties set for database '{label}'")
        else:
            typer.secho("Failed to update properties", err=True, fg='yellow')

# Create an instance to be imported by other modules
page = NotionPage()