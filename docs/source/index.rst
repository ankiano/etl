.. etl-tool documentation master file, created by
   sphinx-quickstart on Sat Mar 25 23:29:51 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

etl-tool's documentation
====================================

About project.

Getting started
---------------
Install application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Install additional source extentions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   Some note.
   You can learn more about :doc:`our two different sites </choosing-a-site>`.


Keys decsription
---------------

.. figure:: /_static/options-scheme.jpg
   :width: 80%
   :align: center
   :alt: Options scheme

``--help``
  Short help about commands
``--source``
  you can setup different kind of sources
``--extract``
  Optional key for databases. Able to run query and get result.
  You can pass query like string ``select * from table``.
  Or paht to query file ``sql/query.sql``
``-execute``
   Optional key for databases, 
   when you need run query without result, e.x. ``drop table my_table``


.. toctree::
   :maxdepth: 2
   :install: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
