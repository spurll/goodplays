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

* Whenever tags are displayed, make them links to bring up all games that have plays with that tag
* Icon idea: NES controller?
* Allow users to add games not in Giant Bomb:
    * Only viewable by the user who added it?
    * Button to link it to Giant Bomb?
* Ability to delete a game (if logged in and it has no plays)
* Ability to edit a game (if logged in and not linked to GB)
* User management (sign up page, place to change email address, forgot password link)

Known Bugs
----------

* Page resizing in base.html needs to be reworked
* There's no pagination for search results, displaying games, or displaying plays (most important)

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

JQuery and JQuery UI elements included under the [MIT "Expat" License](https://opensource.org/licenses/MIT).

Search makes use of [Giant Bomb's API](https://www.giantbomb.com/api/). Thanks, [Giant Bomb](https://www.giantbomb.com/)!

Remember: [GitHub is not my CV](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/).

