Usage
=====

A quick guide how to install and configure `awm`.

Installation
++++++++++++

virtual environment
-------------------

`awm` can be installed into a python virtual environment::

  $ virtualenv venv
  $ source venv/bin/activate
  $ pip install git+https://github.com/toabctl/awm.git

The available service (`awm-crawler` and `awm-persister`) are now
available in `$PATH` and can be executed.

RPM packages
------------

There are also prebuilt RPM packages (currently openSUSE only)
on the OpenBuildService available::

  https://build.opensuse.org/project/show/home:tbechtold:awm

The RPM packages contain a system user, systemd service files
and a configuration file in :file:`/etc/awm/config.json`

Configure
+++++++++

`awm-crawler` and `awm-persister` need both a configuration file. The
default path is :file:`~/.config/awm/config.json`. Here's a
example configuration.

.. literalinclude:: ../../awm.config.json
   :language: JSON

Most of the `kafka` and `persister` options should be
self-explanatory.

.. note::
   the kafka topic configured with `topic_name` must already
   exist or kafka must be configured to automatically create
   new topics. `awm` will not create the topic.

.. note::
   the database tables needed by `awm-persister` are
   automatically created but the database itself must
   already exist.

The `crawler` section contains the global check `interval`.
It also contains a map of `urls`. Every url in that map
will be periodically checked.
There is also the possibility to do a regular expression check
against the url response body. That's optional.

Contributing
============

Please use github pull requests against::

  https://github.com/toabctl/awm

Make sure the tests and linters are passing. This is done via TravisCI but
can also be executed locally::

  $ tox -epy38  # for unittests
  $ tox -elint  # for linters (flake8, mypy)
  $ tox -edocs  # for documentation build

