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
        x.max_table_width=round(get_terminal_size().columns*0.8)
        x.field_names = ["Index", "Name"]
        x.align["Name"] = "l"
        pages_dict = {}
        for key in toml_helper.get_db_keys():
            index, x, pages_dict = page.query(key, index, x, pages_dict)
        typer.echo(x)

        toml_helper.set_dict(pages_dict, toml_helper.pages_file)

    
    def all(database):
        
        properties_list = ["Index"] + toml_helper.get_db_prop(database)
        if len(properties_list) ==1:
            properties_list.append("Name")
        
        x = PrettyTable()
        x.max_table_width=round(get_terminal_size().columns*0.95)
        x.field_names = properties_list

        x.align = "l"

        index, x, pages_dict = page.query(database, x = x, properties_list=properties_list)

        typer.echo(x)

        toml_helper.set_dict(pages_dict, toml_helper.pages_file)

    def query(database, index = 0, x = PrettyTable, pages_dict = {}, show_properties=True, properties_list = ["Index", "Name"]):
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
                            "created_time": "created_time",
                            "number": "number",
                            "url": "url",
                            "last_edited_time": "last_edited_time",
                            "checkbox":"checkbox",
                            "phone":"phone_number",
                            "mail":"email",
                            "formula":"formula",
                            "created_by":"created_by",
                            "last_edit": "last_edited_by",
                            "date":"date",
                            "people":"people",
                            "files":"files"
                        }
                        row={p:"" for p in properties_list}
                        row["Index"]= (index)
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
                                #created_by
                                elif type_of == prop_types["created_by"]:
                                    path=properties.get(property).get(prop_types["created_by"])
                                    if path is not None:
                                        row[property] = path.get("name")
                                #date
                                elif type_of == prop_types["date"]:
                                    path=properties.get(property).get(prop_types["date"])
                                    full_string = ""
                                    if path is not None:
                                        start = path.get("start")
                                        end = path.get("end")
                                        if start is not None:
                                            full_string += str(start)
                                            if end is not None:
                                                full_string += " -> "

                                        if end is not None:
                                            full_string += str(end)                              

                                    row[property] = full_string
                                #last_edit
                                elif type_of == prop_types["last_edit"]:
                                    path=properties.get(property).get(prop_types["last_edit"])
                                    if path is not None:
                                        row[property] = path.get("name")
                                #formula
                                elif type_of == prop_types["formula"]:
                                    path=properties.get(property).get(prop_types["formula"])
                                    if path is not None:
                                        row[property] = path.get("number")
                                #multi-select
                                elif type_of == prop_types["multi"]:
                                    path=properties.get(property).get(prop_types["multi"])
                                    full_string = ""
                                    for p in path:
                                        full_string += p.get("name") + " "
                                    row[property] = full_string
                                #files
                                elif type_of == prop_types["files"]:
                                    path=properties.get(property).get(prop_types["files"])
                                    full_string = ""
                                    for p in path:
                                        full_string += p.get("name") + " "
                                    row[property] = full_string
                                #people
                                elif type_of == prop_types["people"]:
                                    path=properties.get(property).get(prop_types["people"])
                                    full_string = ""
                                    for p in path:
                                        full_string += p.get("name") + " "
                                    row[property] = full_string
                                #created_time
                                elif type_of == prop_types["created_time"]:
                                    path=properties.get(property).get(prop_types["created_time"])
                                    row[property] = path
                                #last_edited_time
                                elif type_of == prop_types["last_edited_time"]:
                                    path=properties.get(property).get(prop_types["last_edited_time"])
                                    row[property] = path
                                #phone
                                elif type_of == prop_types["phone"]:
                                    path=properties.get(property).get(prop_types["phone"])
                                    row[property] = path
                                 #email
                                elif type_of == prop_types["mail"]:
                                    path=properties.get(property).get(prop_types["mail"])
                                    row[property] = path
                                #number
                                elif type_of == prop_types["number"]:
                                    path=properties.get(property).get(prop_types["number"])
                                    if path is None:
                                        row[property] = ""
                                    else:
                                        row[property] = path
                                #checkbox
                                elif type_of == prop_types["checkbox"]:
                                    path=properties.get(property).get(prop_types["checkbox"])
                                    if path is True:
                                        row[property] = "[x]"
                                    else:
                                        row[property] = "[ ]"
                                #url
                                elif type_of == prop_types["url"]:
                                    path=properties.get(property).get(prop_types["url"])
                                    if path is None:
                                        row[property] = ""
                                    else:
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

    def set_database(key, id):
        db_dict = toml_helper.get_dict(toml_helper.config_file)
        
        if "databases" not in db_dict.keys():
            db_dict["databases"] = {}
        
        db_dict.get("databases")[key] = {"id": id} 

        toml_helper.set_dict(db_dict, toml_helper.config_file)
        
        properties = api_helper.get_db_props(api_helper, id)

        return list(properties)



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

    def get_properties(label):
        return list(api_helper.get_db_props(api_helper, toml_helper.get_db_id(label)))
    
    def show_properties(properties):
        x = PrettyTable()
        x.field_names = [i for i in range (0, len(properties))]
        x.add_row(properties)
        return x
    
    def set_properties(label, properties):
        db_dict = toml_helper.get_dict(toml_helper.config_file)
        
    
        db_dict.get("databases")[label]["properties"] = properties
        
        toml_helper.set_dict(db_dict, toml_helper.config_file)
