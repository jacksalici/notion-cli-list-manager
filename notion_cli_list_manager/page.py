from os import get_terminal_size
import typer
from .utils import api_helper, toml_helper
from prettytable import PrettyTable



class page():

    def add(title, database):
        api_helper.new_page(api_helper, title, database)

    def all_by_all():
        index = 0
        x = PrettyTable()
        x.field_names = ["i", "Name"]
        x.align["i"] = "r"
        x.align["Name"] = "l"
        pages_dict = {}
        for key in toml_helper.get_db_keys():
            index, x, pages_dict = page.query(key, index, x, pages_dict)
        typer.echo(x)

        toml_helper.set_dict(pages_dict, toml_helper.pages_file)

    
    def all(database):
        properties_list = ["i"] + toml_helper.get_db_prop(database)
        if len(properties_list) ==1:
            properties_list.append("Name")
        
        x = PrettyTable()
        
        x.field_names = properties_list
        x.align = "l"
        x.align["i"] = "r"
        index, x, pages_dict = page.query(database, x = x, properties_list=properties_list)

        typer.echo(x)

        toml_helper.set_dict(pages_dict, toml_helper.pages_file)

    def query(database, index = 0, x = PrettyTable, pages_dict = {}, show_properties=True, properties_list = ["i", "Name"]):
        r = api_helper.get_pages(api_helper, database)

        if type(r) is dict:
            if r["object"] == "list":
                for page in r["results"]:
                        properties = page.get("properties")
                        prop_types = {
                            "title": "title",
                            "rich": "rich_text",
                            "select": "select",
                            "multi": "multi_select",
                            "created_time": "created_time"
                        }
                        row={p:"" for p in properties_list}
                        row["i"]= index
                        for property in properties:
                            if property in row.keys():
                                type_of = properties.get(property).get("type")
                                #title
                                if type_of == prop_types["title"]:
                                    path=properties.get(property).get(prop_types["title"])
                                    if len(path)>0:
                                        row[property] = path[0].get("text").get("content")
                                #rich-text
                                elif type_of == prop_types["rich"]:
                                    path=properties.get(property).get(prop_types["rich"])
                                    full_string = ""
                                    for p in path:
                                        full_string += p.get("plain_text")
                                    row[property] = full_string
                                #select
                                elif type_of == prop_types["select"]:
                                    path=properties.get(property).get(prop_types["select"])
                                    if path is not None:
                                        row[property] = path.get("name")
                                #multi-select
                                elif type_of == prop_types["multi"]:
                                    path=properties.get(property).get(prop_types["multi"])
                                    full_string = ""
                                    for p in path:
                                        full_string += p.get("name") + " "
                                    row[property] = full_string
                                #created_time
                                elif type_of == prop_types["created_time"]:
                                    path=properties.get(property).get(prop_types["created_time"])
                                    row[property] = path
                                else:
                                    row[property] = "NS"

                        x.add_row(row.values())    
                        pages_dict[str(index)] = page
                        index+=1

            elif r["object"] == "error":
                typer.echo("Error:\t" + str(r["message"]))
                

        return index, x, pages_dict


    def remove(list_of_indexes):
        pages_dict = toml_helper.get_dict(toml_helper.pages_file)
        for index in list_of_indexes:
            p = pages_dict.get(str(index))
            if type(p) == dict:
                api_helper.remove_page(api_helper, p.get("id"))

    def set_token(token):
        dict = toml_helper.get_dict(toml_helper.config_file)
        dict["token"] = token
        toml_helper.set_dict(dict, toml_helper.config_file)

    def set_database(key, id, get_tags = True):
        db_dict = toml_helper.get_dict(toml_helper.config_file)
        
        if "databases" not in db_dict.keys():
            db_dict["databases"] = {}
        
        db_dict.get("databases")[key] = {"id": id} 


        if get_tags:
            db_dict.get("databases")[key]["properties"] = api_helper.get_db_props(api_helper, id)
        
        toml_helper.set_dict(db_dict, toml_helper.config_file)

    def show_databases():
        list = toml_helper.get_db_keys()
        x = PrettyTable()
        x.field_names = ["Label"]
        for label in list:
            x.add_row([label])
        typer.echo(x)

    def rm_database(label):
        dict = toml_helper.get_dict(toml_helper.config_file)
        r = dict.get("databases").pop(label)
        toml_helper.set_dict(dict, toml_helper.config_file)

    
