### Installation:
    sudo apt install python3-dev python3-pip libsasl2-dev
    sudo pip3 install git+https://github.com/ankiano/etl.git -U

### Examples of usage:

    etl --help
    
    etl --source dbname --extract my-query.sql --target some-gsheet-workbook!my-sheet
    etl --source db1,db2 --extract cube.sql --target xls
    etl --source some.csv --target some-new.xls
    etl --source db1 --extract my-query.sql --target db2 --load scema.table_my_query

### Options syntax scheme:
![img_alt](etl-options-scheme.jpg)

### Configurating:

Config `.etl.yml` searching priorities:

1. by option `--config /somepath/.etl.yml`
2. by default in home directory
3. by enviroment variable "ETL_CONFIG"
    ```sudo echo "export ETL_CONFIG=~/etl.yml" > /etc/profile.d/etl.sh```
4. if nothing found, then will be created default config with some examples

Gspreadsheets token `.gsheet-credentials.json` searching priorities: 
1. by setting path in `.etl.yml`
2. by default in home directory

### Hive dependencies:
For conection to hive thrift server you might need install

    sudo apt-get install libsasl2-dev
    
For Windows it's also possible, but with some difficults:
1. Instead `sasl` you might install `pure-sasl`
2. Replace some code in [`pyhive/hive.py`](https://github.com/dropbox/PyHive/pull/122/commits/9662233072f8d64dfca8d4babe0ddf9bac003536)
3. Replace some code in [`thrift_sasl/___init.py___`] (https://github.com/cloudera/impyla/issues/238)
