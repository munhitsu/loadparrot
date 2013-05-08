Short introduction to loadParrot
================================
An experiment to make ultra scalable and fast load testing
tool for HTTP.

It's based on: `ØMQ <http://zeromq.org>`_, python and gevent.

Status
------
proof of concept

Requirements
------------
1. As user I shall be able to test real traffic on remote website
2. As user I shall be able to distribute traffic among huge cluster
3. As user I shall be able to easily use scenarios from tsung, preferably whole configurations
4. As user I shall be able to run test on clusters within minutes (simple deployment)

Install
-------
1. Clone git repo::

    git clone https://github.com/munhitsu/loadparrot.git

2. Create and enter virtual env. My favourite method is by using
   virtualenv wrapper. See: `gist <https://gist.github.com/1034876>`_

3. Install all C dependencies. In case of osx `homebrew <http://mxcl.github.io/homebrew/>`_ seems to be a reliable package manager. ::

    $ brew install libevent
    $ brew install zeromq

4. Install all python dependencies::

    cd loadparrot
    pip install -r requirements.txt
    add2virtualenv .

5. Repeat on all hosts that you want to run workers

Usage
-----
1. Start workers pointing to kings ip::

    python loadparrot/worker.py --king (king_ip)

2. As a temporary hack edit scenario in loadparrot/scenario.py
3. Start the king::

    python loadparrot/king.py

Documentation
-------------
Sphinx based. To build execute make within docs directory.

TODO
----
-  unit tests
-  real configuration instead of stubs
-  read real metrics
-  spawn http stats interface
-  print charts (preferably in browser)
-  update user events execution to be based on a Poisson Distribution or
   other :)
-  optimize scenarios

   -  client should pull all scenarios from server on start
   -  we shall request execution of scenario with specific version
   -  if client uses different scenario version than it shall pull a
      latest version
   -  each execution of parent should generate unique version so we can
      run workers and restart king
   -  flush queues (handbrake) so that king can restart and we don't
      need to restart workers

-  fab + buildout/virtualenv for easy remote deploy and start
-  rename king to... queen

