.. etl-tool documentation master file, created by
   sphinx-quickstart on Sat Mar 25 23:29:51 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ETL tool documentation
=================

Overview
========

ETL is a lightweight command-line tool for extracting, transforming, and loading data from various sources. 
Inspired by the simplicity of SQLite or DuckDB databases, ETL aims to provide a simple, easy-to-use tool for ETL tasks that can be easily set up with just a few commands without the need for complex tools or programming.
ETL allows users to extract data from a variety of sources, including CSV, JSON, XML, Excel, SQL databases, and Google Sheets. 
The lightweight nature of ETL makes it ideal for small to medium-sized projects, where a more heavyweight ETL tool may be overkill. 
In this documentation, we will cover how to install and use ETL, as well as provide examples and best practices.


Installation
============

Install the ``etl`` package

.. code:: console

   $ pip3 install git+https://github.com/ankiano/etl.git




Installation
============

Prerequisites
-------------

Before installing ETL, you will need the following:

- Git (https://git-scm.com/)
- Python 3.9 or higher (https://www.python.org/downloads/)
- pip (https://pip.pypa.io/en/stable/installing/)


Installing with pip
-------------------

The easiest way to install ETL is to use pip, the Python package installer. Simply run the following command in your terminal:

.. code-block:: console

   $ pip install git+https://github.com/ankiano/etl.git
   $ pip install git+https://github.com/ankiano/etl.git -U
   $ sudo -H pip install git+https://github.com/ankiano/etl.git -U

This will install the latest version of ETL from the GitHub repository.

.. tip::

   To install python on Windows it is make sence to use Anaconda3 package (https://www.anaconda.com)

Install additional source extentions
-------------------
`etl` uses `SQLAlchemy` engine for connect to many source.
So you can connect to any source additionaly install dialects extentions.


Installing additional dialects
-------------------------------

`etl` uses the `SQLAlchemy` engine to connect to many different sources, and supports additional dialects for connecting to specific databases. 
Here are some of the SQL databases and sources supported by SQLAlchemy:

+-------------+-------------------------------------------------------+
| Dialect     | Install command                                       |
+=============+=======================================================+
| PostgreSQL  | ``pip3 install psycopg2-binary``                       |
+-------------+-------------------------------------------------------+
| Oracle      | ``pip3 install cx_Oracle``                            |
+-------------+-------------------------------------------------------+
| MySQL       | ``pip3 install mysqlclient``                           |
+-------------+-------------------------------------------------------+
| SQL Server  | ``pip3 install pyodbc``                                |
+-------------+-------------------------------------------------------+
| SQLite      | ``pip3 install pysqlite3``                             |
+-------------+-------------------------------------------------------+
| DuckDB      | ``pip3 install duckdb-engine``                     |
+-------------+-------------------------------------------------------+
| Presto      | ``pip3 install presto-python-client sqlalchemy_presto`` |
+-------------+-------------------------------------------------------+
| Hive        | ``pip3 install pyhive[hive]``                          |
+-------------+-------------------------------------------------------+

Google sheets connection realise in etl package using api.

.. note::
   Note that you will need to have the appropriate drivers installed for the dialect to work properly. 
   Additionally, some dialects may require additional configuration, such as providing connection parameters. 
   Please refer to the `SQLAlchemy dialects documentation <https://docs.sqlalchemy.org/en/20/dialects/index.html#dialects>`_ for more information on configuring dialects.


Setup config file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. tip::
    We recommend that you

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
