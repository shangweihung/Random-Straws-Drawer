# Random-Straws-Drawer
This is a side project that I use for gaining knowledge on web development and database implementation. Functions and User Interface are keep updating and adjusting. 

## Purpose:

Provide a system for user to randomly pick up members in database by some condition. Besides, the members can be added from web. 

## File Structure
```
Root
|
|    create_db.sql              Database Schema Definition
|    main.py                    Implement all functions in web
|    members.csv                Members list prototype
|    write_db.py                Write the first database
|    members.db                 Database example after run write_db.py
|    config.ini
|    README.md
|
+----templates                  Save html files
|   | base.html
|   | index.html                Main Page                 
|   | draw.html                 Draw Straw
|   | history.html              Show history record        
|   | addmember.html            Add new member
|   | showmember.html           Show current member list
|   | login.html                (To be continued)
```

## Required packages
**Python version**: `3.7.3`
**Development Environment**: `Ubuntu 18.04`

#### 1. flask   <--- tvim
#### 2. sqlite3
#### 3. random
#### 4. csv
#### 5. datetime 
#### 6. traceback


## How to view this system?
#### 1. `members.db` is provided. If not provided, run `write_db.py` first.
#### 2. Run `main.py`
#### 3. Open browser, Type `localhost:5000` or `http://127.0.0.1:5000/`
