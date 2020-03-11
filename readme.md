Goodplays
=========

A web application that tracks games played.

Usage
=====

Requirements
------------

* flask
* flask-login
* flask-wtf
* flask-sqlalchemy
* sqlalchemy 1.1
* requests
* ldap3

Configuration
-------------

You'll need to create a `config.py` file, which specifies details such as which LDAP
server to use. A sample configuration file can be found at `sample_config.py`.

Starting the Server
-------------------

Start the server with `run.py`. By default it will be accessible at `localhost:9999`. To
make the server world-accessible or for other options, see `run.py -h`.

If you're having trouble configuring your sever, I wrote a
[blog post](http://blog.spurll.com/2015/02/configuring-flask-uwsgi-and-nginx.html)
explaining how you can get Flask, uWSGI, and Nginx working together.

Bugs and Feature Requests
=========================

Feature Requests
----------------

* Polishes:
    * Sort "interested" games by release date (desc)
    * On Details page, the "add play" row should be at the bottom (not top) of the table
    * Whenever tags are displayed, make them links to bring up all games that have plays
      with that tag
    * Allow user to select sort order for plays and games
    * Add some way to view only games completed in a specific year (like a Goodreads
      reading challenge)
    * Search should autofocus (at least on the search page), and should remain populated
      with the most recent search
    * Instead of a dropdown, each of the five stars should be clickable to set the rating
      to its level (with zero stars having low opacity and showing "No Rating" behind it)
* Add a "played" status for games that don't really define completion (racing games,
  fighting games, etc.)
* Define a `Play.is_completed` attribute (status is "played", "completed", or "100%") and
  add that filter to Plays screen
* User management (change email address, name, password, forgot password)
* For games not in Giant Bomb, provide a way to link them to Giant Bomb?

Known Bugs
----------

* Sign up and other user management functions are not supported for LDAP

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

JQuery and JQuery UI elements included under the [MIT "Expat" License](https://opensource.org/licenses/MIT).

Search makes use of [Giant Bomb's API](https://www.giantbomb.com/api/). Thanks, [Giant Bomb](https://www.giantbomb.com/)!

Remember: [GitHub is not my CV](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/).

