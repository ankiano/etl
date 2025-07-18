ETL tool documentation
######################

Overview
========

`etl` is a lite command-line tool for extracting, transforming, and loading data from various sources. 
Inspired by the simplicity of SQLite or DuckDB databases, `etl` aims to provide a simple, easy-to-use tool for tasks that can be easily set up with just a few commands without the need for complex tools or programming.
`etl` allows users to extract data from a variety of sources, including CSV, JSON, XML, Excel, SQL databases, and Google Sheets. 
The lightweight nature of `etl` makes it ideal for small to medium-sized projects, where a more heavyweight `etl` tool may be overkill.
In this documentation, we will cover how to install and use `etl`, as well as provide examples and best practices.

`https://github.com/ankiano/etl <https://github.com/ankiano/etl>`_

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

   $ pip3 install git+https://github.com/ankiano/etl.git
   $ pip3 install git+https://github.com/ankiano/etl.git -U # update version if exists 
   $ sudo -H pip3 install git+https://github.com/ankiano/etl.git -U # install to system level

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
     - ``sudo -H pip3 install psycopg2-binary``
   * - Oracle
     - ``sudo -H pip3 install cx_Oracle``
   * - MySQL
     - ``sudo -H pip3 install mysqlclient``
   * - MS SQL Server
     - ``sudo -H pip3 install pymssql``
   * - SQLite
     - ``sudo -H pip3 install pysqlite3``
   * - DuckDB
     - ``sudo -H pip3 install duckdb-engine``
   * - Presto
     - ``sudo -H pip3 install presto-python-client sqlalchemy_presto``
   * - Hive
     - ``sudo -H pip3 install pyhive[hive]``
   * - Clickhouse
     - ``sudo -H pip3 install clickhouse-driver==0.2.6 clickhouse-sqlalchemy==0.2.3``


Google sheets connection realised by `pygsheets <https://pygsheets.readthedocs.io/en/stable/>`_ 
Files (csv, xlsx, parquet, xml) input and output realised by `pandas <https://pandas.pydata.org/docs/reference/io.html>`_ functionality. 

.. note::
   Note that some dialects may require additional configuration or to have the appropriate drivers or client installed. 
   Please refer to the `SQLAlchemy dialects documentation <https://docs.sqlalchemy.org/en/20/dialects/index.html#dialects>`_ for more information on configuring dialects.


Usage instructions
==================
`etl` can be accessed from the terminal or console. 
You can also create shell or batch files that contain ETL commands, which can then be scheduled to run at specific intervals using tools like cron. 


Options list
-----------

.. figure:: /_static/options-scheme-white.png
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
``--config-path``
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


Use cases
---------
These examples show how to use 'etl' in a variety of situations.
This will help understand how to integrate your project into their own projects.

1) Shell command files

  Usefull to run and repeat `etl` commands put it in `update.sh` file.
  You can build simple pipelines using `etl` several times and using files or local database for intermidiate result saving.
  
  .. code-block:: concole
    :caption: update.sh
    :linenos:
    
    #! /bin/bash

    etl --source database_a --extract data-1.sql --target local --load main.data_1
    etl --source database_b --extract data-2.sql --target local --load main.data_2
    
    elt --source local --extract 'select * from data_1 t join data_2 d on t.key=d.key' \
        --target result.xlsx


2) Internet datasets
  
  For data playing perspective it is easy to recive famous dataset from Internet.

  .. code-block:: concole
    :caption: update.sh
    :linenos:
    
    #! /bin/bash

    dataset_file='https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv'
    etl --source "$dataset_file??sep=," \
        --target input/titanic.xlsx

3) Report or dashboard update in google sheets

  We can build quick report and dashboards using google sheets. 
  You just need create worbook, share this book to technical email in `.google-api.key.json` and use `etl` to upload data to needed sheet.
  If sheet not exists, `etl` create it automaticaly.
  If you will load data several times, `etl` erase each time values from sheet and insert new data.
  
  .. code-block:: concole
    :caption: update.sh
    :linenos:
    
    #! /bin/bash

    etl --source some_db --extract sql/query.sql \
        --target gsheet --load some-gsheet-workbook!my-sheet

4) Report or dashboard update in sharepoint or onedrive business excel

  Also We can build quick report and dashboards using excel.
  You have to configure `.ms-api-key.yml` (you can find details in Configurating chapter)
  Then you can create worbook and use `etl` to upload data to needed sheet.
  If sheet not exists, `etl` create it automaticaly.
  If you will load data several times, `etl` erase each time values from sheet and insert new data.
  
  .. code-block:: concole
    :caption: update.sh
    :linenos:
    
    #! /bin/bash

    #workbook='users/john.do@organization.org/drive/root:/report.xlsx:' #onedrive
    workbook='sites/381b6266-d315-4e73-a947-65742ed52999/drive/root:/report.xlsx:' #sharepoint

    etl --source some_db --extract sql/query.sql \
        --target sharepoint --load "$workbook??sheet_name=_query"

  You can setup path to excel file with different notations::
- OneDrive Business : ``/users/john.do@organizaion.org/drive/root:/Test/Book1.xlsx:``
- Sharepoint Sites: ``/sites/{site-id}/drive/root:/Sales/Book2.xlsx:``
| To find site-id you can open url like ``https://organizaion.sharepoint.com/sites/{site-name}/_api/site/id``

5) Parameters inside sql query
  
  It is possibility to use parameters inside of sql. 
  In sql you should place parameter in python format ``select * from table where param = {user_sql_parameter}``
  And add option key with name of this custom parameter to update query with value.

  .. code-block:: concole
    :caption: update.sh
    :linenos:
    
    #! /bin/bash

    etl --source some_db --extract sql/query-template.sql \
        --user_sql_parameter 123 \
        --target output/result.xlsx

6) Avoiding limit with google api

  Google api has per-minute quotas, request limit of 300 per minute per project.
  You can extend this limit using several api keys at the same time. 
  You have to setup one alias name but with different keys files.
  Each time `etl` runs will select one of them randomly.

  This technique can also be used to load balance across identical relational database replica instances.

.. code-block:: yaml
   :caption: .etl.yml
   :linenos:

   gsheet: 'google+sheets://??credentials=~/.google-api-key-1.json'
   gsheet: 'google+sheets://??credentials=~/.google-api-key-2.json'
   gsheet: 'google+sheets://??credentials=~/.google-api-key-3.json'

7) Loading a set of similar files

  Sometimes you have a lot of files to process. 
  
  .. code-block:: concole

    ├── input
        ├── file1.csv
        ├── file2.csv
        ├── file3.csv
        └── file4.csv
  
  Using native bash loop end `etl` can help you.

.. code-block:: concole
    :caption: update.sh
    :linenos:
    
    #! /bin/bash

    for f in input/file*.csv; do
      etl --source "$f" --target local --load main.files_content
    done


Best practices
---------------

Some example of organizing working directory.

.. code-block:: concole

    home
    └── me
        ├── playground
        │   ├── ad-hoc
        |   |   ├── process-set-of-files
        |   │   │   ├── input
        │   │   │   |   ├── file1.csv
        │   │   │   |   ├── file2.csv
        │   │   │   |   ├── file3.csv
        │   │   │   |   └── file4.csv
        |   |   |   ├── local.db
        |   |   |   ├── update.log
        │   │   |   └── update.sh
        │   ├── report
        │   │   ├── demo-dashboard
        │   │   │   ├── sql
        │   │   │   │   └── data-cube.sql
        │   │   │   └── update.sh
        │   │   ├── demo-datafeed
        │   │   │   ├── sql
        │   │   │   │   └── dataset.sql
        │   │   │   ├── update.log
        │   │   │   └── update.sh
        │   │   └── demo-report
        │   │       ├── input
        │   │       │   └── titanic.xlsx
        │   │       ├── sql
        │   │       │   ├── data-dd.sql
        │   │       │   └── data-mm.sql
        │   │       ├── local.db
        │   │       ├── update.log
        │   │       └── update.sh
        │   ├── crontab
        │   └── crontab-update.sh
        ├── .bash_aliases
        ├── .etl.yml
        ├── .google-api-key.json
        └── .ms-api-key.json


- Config files we can store in user directory
- Reports and ad-hoc activities we can store in separated way
- Sheduling plan crontab for update reports we can store in `playground` directory
- All sql query we can put in sql directory
- For each report, dashboard, datafeed we create update.sh with same name

.. code-block:: yaml
   :caption: .etl.yml
   :linenos:

   local: 'duckdb:///local.db' # use this alias when you need local database in project directory
   gsheet: 'google+sheets://??credentials=~/.google-api-key.json' # use this alias to load data to google sheets
   sharepoint: 'microsoft+graph://??credentials=~/.ms-api-key.yml'
   db_alias1: 'sqlite:////home/user/workspace/folder/some.db'
   db_alias2: 'postgres://user:pass@host:port/database'
   db_alias3: 'mysql+pymysql://user:pass@host:port/database?charset=utf8'
   db_alias4: 'oracle+cx_oracle://sys:pass@host:port/database?mode=SYSDBA'
   db_alias5: 'awsathena+rest://aws_access_key_id:aws_secret_access_key@athena.region_name.amazonaws.com:443/schema_name?s3_staging_dir=s3_staging_dir'
   db_alias6: 'clickhouse+http://user:password@host:8443/db?protocol=https'
   db_alias7: 'duckdb:///C:\\Users\\user\\Desktop\\test.duckdb' # windows path style


.. code-block:: console
   :caption: update.sh
   :linenos:

    #!/bin/bash
    
    cd "$(dirname "$0")" # you need this line if you are planning to sheduling it with cron
    
    elt --source local --extract sql/my-query.sql --target output/result.xlsx

.. code-block:: console
   :caption: .bash_aliases
   :linenos:

    # custom alias for run update.sh or other sh with adding logging
    # just type 'upd' and you see running log, after exectuing you will see update.log
    upd () {
      if [[ -z $@ ]]; then
        sh update.sh |& tee update.log
      elif [[ $1 =~ '.sh' ]]; then
        sh $1 |& tee ${1%.sh}.log
      fi
    }


.. code-block:: console
   :caption: crontab
   :linenos:

    # Define enviroment variables
    SHELL=/bin/bash
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/homebrew/bin
    HOME="/home/me/"
    ETL_CONFIG=/home/me/.etl.yml

    ###### test job
    #*/1 * * * * date >./cron.log 2>&1
    #*/1 * * * * printenv >>./cron.log 2>&1
    #*/1 * * * * etl --help >>./cron.log 2>&1

    ###### reports
    # demo-dashboard
    0 6 * * * ./playground/report/demo-report/update.sh >./playground/report/demo-report/update.log 2>&1

.. code-block:: console
   :caption: crontab-update.sh
   :linenos:

    #! /bin/bash

    crontab -l > ./crontab~ #backup current crontab
    crontab ./crontab


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

.. note::
  ``windows C:\Users\user\``
  ``linux \home\user\``
  ``mac \Users\user\`` 

To set up connection to microsoft graph api create file.

.. code-block:: yaml
   :caption: .ms-api-key.yml
   :linenos:

   resource: "https://graph.microsoft.com/v1.0/"
   scopes: ["https://graph.microsoft.com/.default"]
   client_id: "{Application ID}" #you registered in active direvroty application
   authority: "https://login.microsoftonline.com/{Tenant ID}" #you organization tenant id
   secret_id: "{Secret id}"
   client_credential: "{Value}" #of Secret ID

You have to register application in microsoft azure active directory of your organization.
Give permissions on microsoft graph `Sites.ReadWrite.All`, `Files.ReadWrite.All`.

Parameters to source/target
-----------------------------
When connecting to a database using a connection string, you can specify various parameters that customize the connection.
These parameters are appended to the connection string, separated by a ``?`` character and can be combined with ``&``.

- ``?charset=utf8``: Sets the character encoding to UTF-8 for MySQL
- ``?mode=SYSDBA``: Connects to the database using the SYSDBA system privilege for Oracle
- ``?connection_timeout=<seconds>``: Specifies the number of seconds to wait for a connection to be established before timing out for Microsoft SQL Server
- ``?s3_staging_dir=<s3-staging-dir>``: Specifies the Amazon S3 location where query results are stored.
- ``?workgroup=<workgroup-name>``: Specifies the name of the workgroup to use for the connection.

For additional details on the parameters supported by your database, please refer to the official documentation of the corresponding database.

Parameters to Pandas and Engine
------------------------------------------
These parameters are appended to the connection string, separated by a ``??`` character and can be combined with ``&``.

When specifying databases using the ``--source`` and ``--target`` option keys, you can pass additional parameters to the engine.
For example, `??max_identifier_length=128` extend the maximum length of column names when saving to certain database systems.

When specifying files using the ``--source`` and ``--target`` option keys, you can pass additional parameters.
  `to_csv <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html?highlight=to_csv#pandas.DataFrame.to_csv>`_: 
    - ``??header=`` same as header=False, to save data without header
    - ``??sep=;`` specify the column delimiter when loading or saving CSV files
    - ``??low_memory=false`` disable the memory usage optimization for reading large files
  `to_excel <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html>`_: 
    - ``??sheet_name=data`` specify the sheet name to use when saving to an Excel file
    - ``??mode=a`` file mode to use (write or append)
    - ``??engine=openpyxl`` write engine to use, ‘openpyxl’ or ‘xlsxwriter’.

When loading data to databases using the ``--load`` option key, you can pass additional parameters.
  `to_sql <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html?highlight=to_sql>`_: 
    - ``??chunksize=1000`` Specify the number of rows in each batch to be written at a time
    - ``??if_exists=replace`` Drop the table before inserting new values
    - ``??if_exists=append`` (by default) insert new values to the existing table.
    - ``??method=multi`` Pass multiple values in a single INSERT clause

.. toctree::
   :maxdepth: 4
   :caption: Table of Contents

   index
