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
  :linenos:

   $ pip install git+https://github.com/ankiano/etl.git
   $ pip install git+https://github.com/ankiano/etl.git -U # update version if exists 
   $ sudo -H pip install git+https://github.com/ankiano/etl.git -U # install to system level

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


Usage instructions
==================
`etl` can be accessed from the terminal or console. 
You can also create shell or batch files that contain ETL commands, which can then be scheduled to run at specific intervals using tools like cron. 


Option keys
-----------

.. figure:: /_static/options-scheme.png
   :width: 150%
   :align: center
   :alt: Options scheme

``--source``
  You can setup different kinds of sources, such as a filepath, database connection string, or alias from the config file.
``--extract``
  An optional key for databases that allows you to run a query and get the result.
  You can pass the query as a string, e.g. ``select * from table``, or as a path to a query file, e.g. ``sql/query.sql``.
``--execute``
  An optional key for databases that is used when you need to run a query without returning a result, e.g. ``drop table my_table``.
``--target``
   You can setup different kinds of targets, such as a filepath, database connection string, or alias from the config file
``--load``
  Used for loading data to a database to identify which table to load the data into.
``--config-paht``
  A custom path to the etl.yml config.
``--debug``
  Enables an extended level of logging with more information.
``--help``
  Provides short help about the commands.


Quick examples
--------------

Open terminal and try to type commands.

.. code-block:: console
  :linenos:

  etl --help
  etl --source input.csv --target output.xlsx
  etl --source input.csv --target 'sqlite:///local.db' --load main.my_table
  etl --source db_alias --extract my-query.sql --target result.xlsx


Best practices and cases
------------------------
Provide examples of how to use `etl` in real-world scenarios. This will help users understand how to integrate your project into their own projects.

Shell command files

Internet datasets

etl --source 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv??sep=,' --target input/titanic.xlsx


etl --source db_alias2 --extract my-query-template.sql --user_sql_parameter 123 --target output/result.xlsx

etl --source db_alias3 --extract my-query.sql --target gsheet --load some-gsheet-workbook!my-sheet

Report or dashboard update


Parameters inside sql query


Sheduling and logging



Configurating
=============
In order to set up connections to databases, etl uses the connection string format. However, connection strings can be long. 
To save time, etl can find the connection string by its alias in a .etl.yml config file:


.. code-block:: yaml
   :caption: .etl.yml
   :linenos:

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

Parameters to source database
-----------------------------
When connecting to a database using a connection string, you can specify various parameters that customize the connection.
These parameters are appended to the end of the connection string, separated by a ? character. 

- `?charset=utf8`: Sets the character encoding to UTF-8 for MySQL
- `?mode=SYSDBA`: Connects to the database using the SYSDBA system privilege for Oracle
- `?connection_timeout=<seconds>`: Specifies the number of seconds to wait for a connection to be established before timing out for Microsoft SQL Server
- `?s3_staging_dir=<s3-staging-dir>`: Specifies the Amazon S3 location where query results are stored.
- `?workgroup=<workgroup-name>`: Specifies the name of the workgroup to use for the connection.

For additional details on the parameters supported by your database, please refer to the official documentation of the corresponding database.

Parameters to Pandas and Engine
------------------------------------------

In option key `--source` and `--target` when we specifies databases we can trougth parameter for engine.
- `max_identifier_length=128` limit the maximum length of column names when saving to certain database systems

In option key `--source` and `--target` when we specifies files we can additional througt parameters.
`to_csv <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html?highlight=to_csv#pandas.DataFrame.to_csv>`_: 
- `??header=0`: specify the row index to use as column names when loading CSV files
- `??sep=;`: specify the column delimiter when loading or saving CSV files
- `??low_memory=false`: disable the memory usage optimization for reading large files
 
 `to_excel <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html>`_: 
- `sheet_name=data`: specify the sheet name to use when saving to an Excel file
- `mode=a`: specify the mode when saving to an existing Excel file, either 'a' (append) or 'w' (overwrite)
- `engine=openpyxl`: select the engine to use when loading or saving Excel files
In option key `--load` for databases we can additionaly pass
`to_sql <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html?highlight=to_sql>`_: 
- `chunk_size=1000` Specify the number of rows in each batch to be written at a time
- `if_exists=replace`
- `method=multi`


.. toctree::
   :maxdepth: 4
   :caption: Table of Contents

   index
