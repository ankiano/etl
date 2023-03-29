For documentation and full examples, please see the [documentation](https://etltool.readthedocs.io/en/latest/#).

### Installation:
    sudo -H pip3 install git+https://github.com/ankiano/etl.git -U

### Quick examples of usage:

    etl --help

    etl --source 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv??sep=,' --target input/titanic.xlsx
    etl --source 'sqlite:////home/user/my-local.db' --extract my-query.sql --target result.csv
    etl --source db_alias2 --extract my-query-template.sql --user_sql_parameter 123 --target output/result.xlsx
    etl --source db_alias3 --extract my-query.sql --target gsheet --load some-gsheet-workbook!my-sheet
    etl --source input/titanic.xlsx --target 'sqlite:///local.db' --load main.titanic


### Options syntax scheme:
![img_alt](docs/source/_static/options-scheme.png)

### Configurating:

Example of `.etl.yml`:

    local: 'sqlite:///local.db' #relative path, e.x. in the same dir where etl runs
    db_alias1: 'sqlite:////home/user/workspace/folder/some.db' #absolute path
    db_alias2: 'postgres://user:pass@host:port/database'
    db_alias3: 'mysql+pymysql://user:pass@host:port/database?charset=utf8'
    db_alias4: 'oracle+cx_oracle://sys:pass@host:port/database?mode=SYSDBA'
    gsheet: 'google+sheets://??credentials=~/.google-api-key.json'

Config `.etl.yml` searching priorities:

1. by command option `--config /somepath/.etl.yml`
2. by os enviroment variable ```sudo echo "export ETL_CONFIG=~/etl.yml" > /etc/profile.d/etl-config.sh```
3. by default in home directory
4. if nothing found, then will be created default config with some examples
