loadParrot
==========

An experiment to make ultra scalable and extremely fast load testing tool for HTTP
Based on: zeromq/zmq/ØMQ/, python and gevent


Status
------
proof of concept


Requirements
------------
We shall be able to test real traffic on remote website
We shall be able to distribute traffic among huge cluster
We shall be able to easily use scenarios from tsung, preferably whole configurations
We shall be able to run test on clusters within minutes (simple deployment)


TODO
----
- unit tests
- real configuration instead of stubs
- read real metrics
- spawn http stats interface
- print charts (preferably in browser)
- update user events execution to be based on a Poisson Distribution or other :)
- optimize scenarios
  - client should pull all scenarios from server on start
  - we shall request execution of scenario with specific version
  - if client uses different scenario version than it shall pull a
    latest version
  - each execution of parent should generate unique version
    so we can run workers and restart king
- flush queues (handbrake) so that king can restart and we don't need to
  restart workers
- fab + buildout for easy remote deploy and start
