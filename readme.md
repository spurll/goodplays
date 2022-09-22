Goodplays
=========

![Screenshot](/screenshots/plays.png?raw=true)

A web application that tracks games played.

![Details](/screenshots/hltb.png?raw=true)

Usage
=====

Requirements
------------

* flask
* flask-login
* flask-wtf
* flask-sqlalchemy
* sqlalchemy<1.4.0 (sqlalchemy==1.3.24)
* werkzeug<1.0.0 (werkzeug==0.16.1)
* requests
* ldap3

SQLAlchemy version 1.4.0 and Werkzeug version 1.0.0 changed a few bits around, and some of
the dependencies (flask-sqlalchemy, specifically) haven't caught up yet, as of this
writing.

Configuration
-------------

You'll need to create a `config.py` file, which specifies configuration details, such as
authentication information. A sample configuration file can be found at `sample_config.py`.

Starting the Server
-------------------

Start the server with `run.py`. By default it will be accessible at `localhost:9999`. To
make the server world-accessible or for other options, see `run.py -h`.

If you're having trouble configuring your sever, I wrote a
[blog post](http://blog.spurll.com/2015/02/configuring-flask-uwsgi-and-nginx.html)
explaining how you can get Flask, uWSGI, and Nginx working together.

Adding Platforms
----------------

> Hey, why isn't Playdate (for example) listed in the list of platforms when I edit a game?

If you want to add a game from a platform that isn't in the database yet, the easiest way
to do that is to add a game from GiantBomb that is on that platform, then restart
Goodplays with `sudo service uwsgi restart` (assuming you're running it with uWSGI). After
restarting, the new platform should appear in the platform list.

Bugs and Feature Requests
=========================

Feature Requests
----------------

* For games not in Giant Bomb, provide a way to link them to Giant Bomb (`gb_id` field,
  editable just like `hltb_id`)
* Polishes:
    * More/less toggles should be in line with filters when they are visible (not below)
    * Whenever tags are displayed, make them links to bring up all games that have plays
      with that tag
    * Allow user to select sort order for plays and games, and this preference should
      persist (cookie?)
    * On pages with... pages, display the current page number and total number of pages
* Allow admins to upload images in addition to providing links
* User management (change email address, name, password, forgot password)
* Allow users to make their plays public (what would this look like?)

Known Bugs
----------

* Sign up and other user management functions are not supported via LDAP

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

JQuery and JQuery UI elements included under the [MIT "Expat" License](https://opensource.org/licenses/MIT).

Search makes use of [Giant Bomb's API](https://www.giantbomb.com/api/). Thanks, [Giant Bomb](https://www.giantbomb.com/)!

HowLongToBeat integration was inspired by (but does not make use of) ScrappyCocco's [HowLongToBeat Python API](https://github.com/ScrappyCocco/HowLongToBeat-PythonAPI).

Remember: [GitHub is not my CV](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/).

