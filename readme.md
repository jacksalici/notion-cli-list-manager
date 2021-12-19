
#### ⚠️ This project is still in work in progress. Changes to the commands could be done in the future.


# Notion CLI To-Do Manager 🗂
### Increase your productivity with a simple command. 🛋

A simple line-command tool for managing [Notion](http://notion.so) databases of ___ToDo___. You can copy this (link to insert) template.


## Syntax:

| Commands:|    | Args:|
|---|---|---|
| `todo all` | to display all the ___ToDo___ not done yet. |    |
| `todo add [title]` | to add a new ___ToDo___ called `title`. |   `[title]` will be the text of the ___ToDo___ (and the title of the associated Notion database page)  | 
| `todo rm [index]` | to remove the ___ToDo___ with the index `index`.  <br> (Command to call after `todo all`)| `[index]` have to be formatted either like a range and a list, or a combination of these. E.g.: 3,4,6:10:2 will remove pages 3, 4, 6, 8.
| `todo set [token] [database_id]` | to set the token and the Notion Database ID. This must be execute as first command. | You can get the `[token]` as internal api integration here (link to insert). <br> You can get the database id from the database url: notion.so/[username]/`[database_id]`?v=[view_id].  |



## Usage:

1. Install the `pip` module.

### Otherwise

2. Clone the directory. 

Execute the 




## Still toDo:
###### forgive the play on words

- [ ] setter for the db id and the token
- [ ] `rm --all` command arg
- [ ] support for tags
- [ ] improve the code stability
- [ ] http requests async 
