
#### ⚠️ This project is still in work in progress. Commands could change in the future.


# Notion CLI List Manager 🗂
### Increase your productivity with a simple command. 🛋

A simple command-line tool for managing [Notion](http://notion.so) ___List___ databases. You can copy [my free simple template](https://jacksalici.notion.site/d75c9590dc8b4d62a6c65cbf3fdd1dfb?v=0e3782222f014d7bb3e44a87376e3cfb).


## Syntax:

| Commands:|    | Args and options:|
|---|---|---|
| `list` | to display all the ___List___ not done yet. | `--db [id] ` to display a specific database. <br> `--all` to display all the lists.
| `list add [title]` | to add a new ___List___ called `title`. |   `[title]` will be the text of the ___List___ (and the title of the associated Notion database page)  <br> `--db [id] ` to add the entry to a specific database. Otherwise, the default database will be used.| 
| `list rm [index]` | to remove the ___List___ with the index `index`.  <br> _(Command to call after `list all`)_| `[index]` has to be formatted either like a range and a list, or a combination of these. E.g.: 3,4,6:10:2 will remove pages 3, 4, 6, 8.
| `list db` | to display all the notion display saved in the manager. | `--label [LABEL] --id [ID]` to add a database to the manager. <br> `--rm [LABEL]` to remove a database named [LABEL] from the manager. Note that adding or removing a database to the manager does not cause the actual creation or deletion on Notion.
| `list set --token [token] --id [database_id]` | to set the token and the ID of the Notion Database you want as default. _This must be executed as the first command_. | You can get the `[token]` as internal api integration [here](https://www.notion.so/my-integrations). <br> You can get the database id from the database url: notion.so/[username]/`[database_id]`?v=[view_id].  | 
## Usage:

Since it is a beta version, the package it's not available on pypi.org yet. Thus, you have to install it manually.
Having installed Python3 and Pip3 on your machine, write on the terminal:

``` 
    git clone https://github.com/jacksalici/notion-cli-list-manager.git notion-cli-list-manager

    pip3 install notion-cli-list-manager/dist/notion-cli-list-manager-0.1.1.tar.gz

```

Then set the token and the database id:

```
    list set --token [token] --id [database-id]

``` 
_Note that you must share the database with your integration!_
And finally, you can use the commands above.


## Still to do:
See the [project tab](https://github.com/jacksalici/notion-cli-list-manager/projects/1) for a complete and real-time-updated list.

## Collaboration:
Issues and PRs are really appreciated. 


    