ETL tool documentation
######################

Overview
========

`etl` is a lightweight command-line tool for extracting, transforming, and loading data from various sources. 
Inspired by the simplicity of SQLite or DuckDB databases, `etl` aims to provide a simple, easy-to-use tool for `etl` tasks that can be easily set up with just a few commands without the need for complex tools or programming.
`etl` allows users to extract data from a variety of sources, including CSV, JSON, XML, Excel, SQL databases, and Google Sheets. 
The lightweight nature of `etl` makes it ideal for small to medium-sized projects, where a more heavyweight `etl` tool may be overkill. 
In this documentation, we will cover how to install and use `etl`, as well as provide examples and best practices.


Installation
============

Prerequisites
-------------

Before installing `etl`, you will need the following:

- Git (https://git-scm.com/)
- Python 3.9 or higher (https://www.python.org/downloads/)
- pip (https://pip.pypa.io/en/stable/installing/)


Installing with pip
-------------------

The easiest way to install `etl` is to use pip, the Python package installer. Simply run the following command in your terminal:

.. code-block:: console

   $ pip install git+https://github.com/ankiano/etl.git
   $ pip install git+https://github.com/ankiano/etl.git -U #Update version if exists 
   $ sudo -H pip install git+https://github.com/ankiano/etl.git -U #setup to system level

This will install the latest version of ETL from the GitHub repository.

.. tip::
   To install python on Windows it is make sence to use Anaconda3 package (https://www.anaconda.com)


Installing additional dialects
------------------------------

`etl` uses the `SQLAlchemy` engine to connect to many different sources, and supports additional dialects for connecting to specific databases. 
Here are some of the SQL databases and sources supported by `SQLAlchemy`:

.. list-table::
   :header-rows: 1

   * - Dialect
     - Install Command
   * - PostgreSQL
     - ``pip install psycopg2-binary``
   * - Oracle
     - ``pip install cx_Oracle``
   * - MySQL
     - ``pip install mysqlclient``
   * - SQL Server
     - ``pip install pyodbc``
   * - SQLite
     - ``pip install pysqlite3``
   * - DuckDB
     - ``pip install duckdb-engine``
   * - Presto
     - ``pip install presto-python-client sqlalchemy_presto``
   * - Hive
     - ``pip install pyhive[hive]``

Google sheets connection realised by `pygsheets <https://pygsheets.readthedocs.io/en/stable/>`_ 
Files (csv, xlsx, parquet, xml) input and output realised by `pandas <https://pandas.pydata.org/docs/reference/io.html>`_ functionality. 

.. note::
   Note that some dialects may require additional configuration or to have the appropriate drivers or client installed. 
   Please refer to the `SQLAlchemy dialects documentation <https://docs.sqlalchemy.org/en/20/dialects/index.html#dialects>`_ for more information on configuring dialects.

Option keys
================

.. figure:: /_static/options-scheme.png
   :width: 150%
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


Config file
===========
In order to set up connections to databases, etl uses the connection string format. However, connection strings can be long. 
To save time, etl can find the connection string by its alias in a .etl.yml config file:


.. code-block:: yaml
   :caption: .etl.yml

   local: 'sqlite:///local.db'
   db_alias1: 'sqlite:////home/user/workspace/folder/some.db'
   db_alias2: 'postgres://user:pass@host:port/database'
   db_alias3: 'mysql+pymysql://user:pass@host:port/database?charset=utf8'
   db_alias4: 'oracle+cx_oracle://sys:pass@host:port/database?mode=SYSDBA'
   gsheet: 'google+sheets://??credentials=~/.google-api-key.json'


Config .etl.yml searching priorities:

   * by command option ``--config`` `/somepath/.etl.yml`
   * by OS environment variable: ``sudo echo "export ETL_CONFIG=~/etl.yml" > /etc/profile.d/etl-config.sh``
   * by default in user home directory


.. toctree::
   :maxdepth: 4
   :caption: Table of Contents

   index
