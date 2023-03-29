For documentation and full examples, please see the [documentation](https://etltool.readthedocs.io/en/latest/#).

### Installation:
    sudo apt install python3-dev python3-pip
    sudo -H pip3 install git+https://github.com/ankiano/etl.git -U

### Quick examples of usage:

    etl --help

    etl --source db1,db2 --extract cube.sql --target xls
    etl --source some.csv --target some-new.xls
    etl --source db1 --extract my-query.sql --target db2 --load scema.table_my_query
    etl --source db1 --extract my-query-template.sql --target csv --user_sql_parameter 123
    etl --source dbname --extract my-query.sql --target some-gsheet-workbook!my-sheet
    etl --source dbname --extract my-query.sql --target '/users/user_name@tenant/drive/root:/excel-workbook.xlsx:my-sheet'


### Options syntax scheme:
![img_alt](docs/source/_static/options-scheme.jpg)

### Configurating:

Example of `.etl.yml`:

    databases:
        local: 'sqlite:///local.db'
        db_alias1: 'sqlite:////home/user/workspace/folder/some.db'
        db_alias2: 'postgres://user:pass@host:port/database'
        db_alias3: 'mysql+pymysql://user:pass@host:port/database?charset=utf8'
        db_alias4: 'mssql+pymssql://user:pass@host:port/database'
        db_alias5: 'oracle+cx_oracle://user:pass@host:port/database'
        db_alias6: 'oracle+cx_oracle://sys:pass@host:port/database?mode=SYSDBA'

Config `.etl.yml` searching priorities:

1. by command option `--config /somepath/.etl.yml`
2. by os enviroment variable ```sudo echo "export ETL_CONFIG=~/etl.yml" > /etc/profile.d/etl-config.sh```
3. by default in home directory
4. if nothing found, then will be created default config with some examples
