
#### ⚠️ This project is still in work in progress. Commands could change in the future.


# Notion CLI To-Do Manager 🗂
### Increase your productivity with a simple command. 🛋

A simple command-line tool for managing [Notion](http://notion.so) ___ToDo___ databases. You can copy [my free simple template](https://jacksalici.notion.site/d75c9590dc8b4d62a6c65cbf3fdd1dfb?v=0e3782222f014d7bb3e44a87376e3cfb).


## Syntax:

| Commands:|    | Args:|
|---|---|---|
| `todo all` | to display all the ___ToDo___ not done yet. |    |
| `todo add [title]` | to add a new ___ToDo___ called `title`. |   `[title]` will be the text of the ___ToDo___ (and the title of the associated Notion database page)  | 
| `todo rm [index]` | to remove the ___ToDo___ with the index `index`.  <br> (Command to call after `todo all`)| `[index]` has to be formatted either like a range and a list, or a combination of these. E.g.: 3,4,6:10:2 will remove pages 3, 4, 6, 8.
| `todo set [token] [database_id]` | to set the token and the Notion Database ID. This must be executed as the first command. | You can get the `[token]` as internal api integration [here](https://www.notion.so/my-integrations). <br> You can get the database id from the database url: notion.so/[username]/`[database_id]`?v=[view_id].  |



## Usage:

Since it is a beta version, the package it's not available on pypi.org yet. Thus, you have to install it manually.
Having installed Python3 and Pip3 on your machine, write on the terminal:

``` 
    git clone https://github.com/jacksalici/notion-cli-todo-manager.git notion-cli-todo-manager

    pip3 install notion-cli-todo-manager/dist/notion-cli-todo-manager-0.1.0.tar.gz

```

Then set the token and the database id:

```
    todo set [token] [database-id]

``` 

And finally, you can use the commands above.


## Still toDo:
###### forgive the play on words
See the project tab for a more verbose list.

- [ ] `rm --all` command arg
- [ ] support for tags
- [ ] support for more databases
- [ ] support for sigle pages editing
- [ ] improve the code stability
- [ ] http requests async 
