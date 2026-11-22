
##### ⚠️ This project is still in work in progress, please forgive any little flaw here and there.
# Notion CLI List Manager 🗂
A simple command-line tool for managing [Notion](http://notion.so) ___List___ databases. ✨  

### Increase your productivity with a simple command. 🛋

![](showcase.gif)

## 📺 Features:
- fast and clear; saving your idea is as simple as type `add "get money"` 💆‍♂️
- tables are pretty-printed with fab ASCII tables 🌈
- parameters are now supported [^3] 🎻


## 👾 Get Started:
- Create a new internal api integration [here](https://www.notion.so/my-integrations).
- ❗️ Share the default database you want to use with your integration.  
  You can copy [my free simple template](https://jacksalici.notion.site/d75c9590dc8b4d62a6c65cbf3fdd1dfb?v=0e3782222f014d7bb3e44a87376e3cfb).
- Download the tool: [^1]
```
    uv tool install notion-cli-list-manager   # or: pipx install notion-cli-list-manager
```
- Set the token (stored in your system keyring) and your default database id:
```
    list set --token [token] --id [database-id]
``` 
- You're done!

## 🧰 Syntax:
TL;DR: `list` is the keyword for activating this tool from the terminal. Typing just `list`, the list of your default database's items will be shown. Other commands can be used typing `list [command]`

| Commands:|    | Args and options:|
|---|---|---|
| `list` | to display all the ___List___ items. | `--db [id] ` to display a specific database. Otherwise the default database will be shown.<br> `--all` to display all the lists.
| `list add [title]` | to add a new ___List___ item called `title`. |   `[title]` will be the text of the ___List___ item (and the title of the associated Notion database page)  <br> `--db [id] ` to add the entry to a specific database. Otherwise, the default database will be used.| 
| `list rm [index]` | to remove the ___List___ item with the index `index`.  <br> _(Command to call after `list`)_| `[index]` has to be formatted either like a range or a list, or a combination of these. E.g.: 3,4,6:10:2 will remove pages 3, 4, 6, 8.
| `list edit [TITLE]` | to edit the content of the page titled `[TITLE]` as markdown in nano (or `$EDITOR`). Saving the file updates the page. | `--db [LABEL]` picks the database. Child pages and databases are never deleted. |
| `list show configs` | to edit the configuration file in nano (or `$EDITOR`). | It is saved only if it is valid TOML. |
| `list gen [TITLE] --year [YEAR]` | to create one page per day of the year, with its `Date` set. | `[TITLE]` defaults to the date. `--db [LABEL]` picks the database. |
| `list db` | to display all the notion display saved in the manager. | `--label [LABEL] --id [ID]` to add a database to the manager. A prompt will then ask you the ordered indexes list.<br> `--rm [LABEL]` to remove a database named [LABEL] from the manager. Note that adding or removing a database to the manager does not cause the actual creation or deletion on Notion. <br> `--prop [LABEL]` to set which and in which order display the properties of an already saved database labeled [LABEL]. A prompt will then ask you the ordered indexes list[^3].
| `list set --token [token] --id [database_id]` | to set the token and the ID of the Notion Database you want as default. _This must be executed as the first command_. | You can get the `[token]` as internal api integration [here](https://www.notion.so/my-integrations). <br> You can get the database id from the database url: notion.so/[username]/`[database_id]`?v=[view_id]. <br> You can also use separately `--token` and `--id` to set just one parameter. After the `--id` command, a prompt will then ask you the ordered indexes list.   |

## 🛒 Still to do:
See the [project tab](https://github.com/jacksalici/notion-cli-list-manager/projects/1) for a complete and real-time-updated list.    
Issues and PRs are appreciated. 🤝


[^3]: At the present, properties are fully supported (except Relations and Rolls up that are __NS__ - Not supported) but read-only. Writeable ones will be supported in the next versions.

[^1]: You can also clone the repo to have always the very last version.  
With [uv](https://docs.astral.sh/uv/) installed:  
`git clone https://github.com/jacksalici/notion-cli-list-manager.git && cd notion-cli-list-manager`  
`uv run list --help` to run it, `uv run pytest` to test it, `uv tool install .` to install it.




    
