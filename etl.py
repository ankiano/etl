#!/usr/bin/env python3.8
# coding=utf-8

import sys
import os
import logging
import click
import pandas as pd
import numpy as np
import humanize
import pygsheets
import sqlalchemy
from sqlalchemy import event
from cx_Oracle import CLOB
import yaml
import random
import msal
import requests
import urllib


def get_query(sql_file_path):
    try:
        sql_file_path = sql_file_path.replace("\r", "")
        sql = open(sql_file_path, 'r', encoding='utf-8')
        result = " ".join(sql.readlines())
        return sqlalchemy.text(result)
    except Exception as e:
        logging.error(f'Error with reading query, {type(e)}')


def dataframe_size_info_msg(df):
    assert isinstance(df, pd.DataFrame), type(df)
    volume = humanize.naturalsize(df.memory_usage(index=True).sum())
    return f'{volume} of data in {df.size} cells obtained'


def database_extract(**kwargs):
    sql = kwargs.get('sql')
    db_name = kwargs.get('db_name')
    engine = sqlalchemy.create_engine(
                            config.get('databases').get(db_name),
                            max_identifier_length=128,
                            )
    logging.debug(sql)
    result = pd.read_sql(sql=sql, con=engine)
    logging.info(dataframe_size_info_msg(result))
    logging.debug(f'Dataframe columns type:\n{result.dtypes}')
    return result


def database_execute(**kwargs):
    sql = kwargs.get('sql')
    db_name = kwargs.get('db_name')
    engine = sqlalchemy.create_engine(
                            config.get('databases').get(db_name),
                            max_identifier_length=128,
                            )
    logging.debug(sql)
    engine.execute(sql)


def database_load(**kwargs):
    data = kwargs.get('data')
    db_name = options.target

    # Schema name is set
    if options.load.find('.') > 0:
        schema_name = options.load.split('.')[0]
    else:
        schema_name = None

    # Table is not set
    if options.load.endswith('.'):
        table_name = kwargs.get('data_block_name')
    # Table with schema
    elif options.load.find('.') > 0:
        table_name = options.load.split('.')[1]
    # Table without schema
    else:
        table_name = options.load

    engine = sqlalchemy.create_engine(
                            config.get('databases').get(db_name),
                            max_identifier_length=128,
                            # pool_size=20, max_overflow=0
                            # echo=True
                            # echo='debug'
                            )

    @event.listens_for(engine, "do_setinputsizes")
    def _remove_clob(inputsizes, cursor, statement, parameters, context):
        for bindparam, dbapitype in list(inputsizes.items()):
            if dbapitype is CLOB:
                del inputsizes[bindparam]

    data.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False,
        schema=schema_name,
        chunksize=1000
    )
    logging.info(f'Saved data to {schema_name}.{table_name} table')


def csv_extract(**kwargs):
    file_name = kwargs.get('file_name')
    source_file_path = csv_dir + file_name
    result = pd.read_csv(source_file_path, header=0, sep=';', low_memory=False)
    logging.info(dataframe_size_info_msg(result))
    return result


def csv_load(**kwargs):
    if not os.path.exists(csv_dir):
        os.mkdir(csv_dir)
        logging.info('csv folder created')
    data = kwargs.get('data')
    data_block_name = kwargs.get('data_block_name')
    if options.target == 'csv':
        result_file_path = csv_dir + data_block_name + '.csv'
    else:
        result_file_path = csv_dir + options.target
    data.to_csv(result_file_path, sep=';', index=False, encoding='utf-8')
    logging.info(f'Saved data to {result_file_path}')


def xls_extract(**kwargs):
    file_name = kwargs.get('file_name')
    source_file_path = xls_dir + file_name
    result = pd.read_excel(source_file_path, header=0)
    logging.info(dataframe_size_info_msg(result))
    return result


def xls_load(**kwargs):
    if not os.path.exists(xls_dir):
        os.mkdir(xls_dir)
        logging.info('xls folder created')
    data = kwargs.get('data')
    data_block_name = kwargs.get('data_block_name')

    if options.target == 'xls':
        result_file_path = xls_dir + data_block_name + '.xlsx'
    else:
        result_file_path = xls_dir + options.target.split('.')[0] + '.xlsx'

    file_mode = 'a' if os.path.exists(result_file_path) else 'w'
    writer = pd.ExcelWriter(
                            result_file_path,
                            mode=file_mode,
                            date_format='YYYY-MM-DD',
                            datetime_format='YYYY-MM-DD HH:MM:SS'
    )
    if os.path.exists(result_file_path):
        if data_block_name in writer.book.sheetnames:
            writer.book.remove(writer.book[data_block_name])

    logging.debug(f'Dataframe columns type:\n{data.dtypes}')
    data.to_excel(writer, sheet_name=data_block_name,index=False)
    writer.save()
    logging.info(f'Saved data to {result_file_path}')


def spreadsheet_open(workbook_name):
    """
    Authorize google client and open spreadsheet

    """

    # command option --google_api_key
    if os.path.isfile(options.google_api_key):
        key_path = options.google_api_key
        logging.debug(f'Google api key {os.path.abspath(key_path)} found '
                      f'from command option --google_api_key')
    elif (config.get('google_api_keys')
        and options.google_api_key in config.get('google_api_keys').keys()):
        key_path = config.get('google_api_keys')[options.google_api_key]
        logging.debug(f'Google api key {os.path.abspath(key_path)} found '
                      f'from etl.yml config file by alias={options.google_api_key} '
                      f'in command option --google_api_key')
    # os evironment variable GOOGLE_API_KEY
    elif (os.environ.get("GOOGLE_API_KEY")
        and os.path.isfile(os.environ.get("GOOGLE_API_KEY"))):
        key_path = os.environ.get("GOOGLE_API_KEY")
        logging.debug(f'Google api key {os.path.abspath(key_path)} found '
                      f'from os evironment variable GOOGLE_API_KEY')
    # randomly config (etl.yml) google_api_keys:
    elif config.get('google_api_keys'):
        key_path = random.choice(list(config.get('google_api_keys').values()))
        logging.debug(f'Google api key {os.path.abspath(key_path)} was '
                      f'taken randomly from etl.yml config file (google_api_keys:)')
    # from user home dir
    elif os.path.isfile(os.path.expanduser('~/.google-api-key.json')):
        key_path = os.path.expanduser('~/.google-api-key.json')
        logging.debug(f'Google api key {os.path.abspath(key_path)} found '
                      f'from user home dir')
    else:
        logging.error('Google api key file not found. '
                      'Save .google-api-key.json to home directory or'
                      ' set os environment variable (GOOGLE_API_KEY)')
        sys.exit(1)

    # To prevent email printing by pygsheets
    sys.stdout = open(os.devnull, "w")

    gclient = pygsheets.authorize(service_file=key_path,
                                  no_cache=True, retries=10)
    # Switch to normal
    sys.stdout = sys.__stdout__
    try:
        workbook = gclient.open(workbook_name)
    except pygsheets.exceptions.SpreadsheetNotFound:
        logging.error(f'SpreadsheetNotFound error. '
                      f'Share spreadsheet {workbook_name} with service email')
        sys.exit(1)
    return workbook


def gsheet_load(**kwargs):
    """
    Load data to google sheet by name of workbook and by sheet name.

    """
    data = kwargs.get('data')
    if data.size >= 5000000:
        logging.error('Saving to gsheet is ommited due to limit 5M of cells')
        sys.exit(1)

    data = data.fillna('')
    data = data.astype(str)

    workbook_name = options.target.split('!')[0]
    workbook = spreadsheet_open(workbook_name)

    # If exact sheet name was not set
    # then data_block_name will be selected as target sheet name
    sheet_name = kwargs.get('data_block_name') \
        if options.target.endswith('!') else options.target.split('!')[1]

    try:
        sheet = workbook.worksheet_by_title(sheet_name)
        sheet.clear(start='A1')
    except pygsheets.exceptions.WorksheetNotFound:
        sheet = workbook.add_worksheet(sheet_name, rows=1, cols=1)
        logging.info(f'New sheet {sheet_name} added')

    sheet.set_dataframe(data, start="A1", fit=True, nan='')
    logging.info(f'Saved data to {workbook_name}!{sheet_name} spreadsheet')


def gsheet_extract(**kwargs):
    """
    Extract data from google sheet by name of workbook and by sheet name.

    """
    workbook_name = kwargs.get('workbook')
    sheet_name = kwargs.get('sheet')
    workbook = spreadsheet_open(workbook_name)
    sheet = workbook.worksheet_by_title(sheet_name)
    result = sheet.get_as_df()
    logging.info(dataframe_size_info_msg(result))
    return result

def msgraph_open(path):
    """
    Authorize ms google api client and get token

    """

    # command option --msgraph_api_key
    if os.path.isfile(options.msgraph_api_key):
        key_path = options.msgraph_api_key
        logging.debug(f'MS graph api key {os.path.abspath(key_path)} found '
                      f'from command option --msgraph_api_key')
    # os evironment variable MSGRAPH_API_KEY
    elif (os.environ.get("MSGRAPH_API_KEY")
        and os.path.isfile(os.environ.get("MSGRAPH_API_KEY"))):
        key_path = os.environ.get("MSGRAPH_API_KEY")
        logging.debug(f'MS graph api key {os.path.abspath(key_path)} found '
                      f'from os evironment variable MSGRAPH_API_KEY')
    # from user home dir
    elif os.path.isfile(os.path.expanduser('~/.ms-graph-api-key.yml')):
        key_path = os.path.expanduser('~/.ms-graph-api-key.yml')
        logging.debug(f'MS graph api key {os.path.abspath(key_path)} found '
                      f'from user home dir')
    else:
        logging.error('MS graph api key file not found. '
                      'Save .msgraph-api-key.yml to home directory or'
                      ' set os environment variable (MSGRAPH_API_KEY)')
        sys.exit(1)

    # read config from yaml file
    with open(key_path, 'r') as config_file:
        cfg = yaml.safe_load(config_file)

    # create the MSAL confidential client application and require token
    app = msal.ConfidentialClientApplication(
        client_id = cfg['client_id'],
        authority=cfg['authority'],
        client_credential=cfg['client_credential']
        )
    token_response = None
    token_response = app.acquire_token_for_client(scopes=cfg['scopes'])
    if token_response.get('error_description'):
        logging.error(f"MS graph api error: {token_response['error_description']}")
        sys.exit(1)
    return token_response,cfg


def msgraph_load(**kwargs):
    """
    Load data to ms graph api excel by name of workbook and by sheet name.

    """
    def api_call(method, url, body=None):
        http_headers = {'Authorization':  token_response['access_token'],
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        endpoint = urllib.parse.urljoin(cfg['resource'],url.lstrip('/'))
        logging.debug(f'endpoint: {endpoint}')
        return method(endpoint, headers=http_headers, json=body)

    def colnum_string(n):
        '''
        >>> colnum_string(28)
        >>> AB
        '''

        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

    data = kwargs.get('data')
    data = data.fillna('')
    data = data.astype(str)

    workbook_url = options.target.rsplit(':',1)[0]+":"
    token_response, cfg = msgraph_open(workbook_url)
    # If exact sheet name was not set
    # then data_block_name will be selected as target sheet name
    sheet = kwargs.get('data_block_name') \
        if options.target.endswith(':') else options.target.rsplit(':',1)[1]

    # try to add worksheet
    url = workbook_url + f'/workbook/worksheets'
    response = api_call(requests.post, url, {"name": f"{sheet}"})
    if response.status_code == 201:
        logging.info(f'New sheet {sheet} added')

    # clear all worksheet range
    url = workbook_url + f"/workbook/worksheets/{sheet}/range(address='A:XFD')/clear"
    response = api_call(requests.post, url, {"applyTo": "All"})
    response

    # add new table
    url = workbook_url + f"/workbook/worksheets/{sheet}/tables/add"
    col_range = 'A1:%s1' % colnum_string(len(data.columns))
    response = api_call(requests.post, url, {"address": f"{col_range}","hasHeaders": True, "name": sheet}).json()
    table_id = response.get('id')
    if response.get('error'):
        logging.error(f"{response['error']['code']}: "\
                      f"{response['error']['message']}")
        sys.exit(1)

    # add table header
    url = workbook_url + f"/workbook/worksheets/{sheet}/range(address='{col_range}')"
    body = {'values': [data.to_dict(orient='split')['columns']]}
    response = api_call(requests.patch, url, body)

    # add rows by chanks
    chunksize = 1000
    for g, df in data.groupby(np.arange(len(data)) // chunksize):
        url = workbook_url + f'/workbook/tables/{table_id}/Rows'
        body={'values': df.to_dict(orient='split')['data']}
        response = api_call(requests.post, url, body)

    if response.status_code == 201:
        logging.info(f'Saved data to {workbook_url} on {sheet} sheet')


def define_source_type(source):
    """
    Define implicitly given source type by indirect evidence.
    database_name
    file.csv
    csv
    file.xls
    xls
    work-book!sheet-name

    @param source: -- data from --source option

    """
    if source in config.get('databases'):
        return 'database'
    elif source.endswith('.csv'):
        return 'csv'
    elif source.find('.xlsx:') > 0:
        return 'msgraph'
    elif source.endswith('.xls') or source.endswith('.xlsx'):
        return 'xls'
    elif source == 'csv':
        return 'csv'
    elif source == 'xls':
        return 'xls'
    elif source.find('!') > 0:
        return 'gsheet'
    else:
        logging.error(f'Data source {source} is not recognized')
        return 'not specified'


def define_target_name(source):
    """
    Define name from different indirect rules.
    The order of the conditions is very important
    :param source:
    :return: name for target data block name
    """
    # The first priority is query_name and it has defined in main()
    name = 'default_name'

    # Exact table name
    if options.target in config.get('databases') \
            and options.load.find('.') > 0:
        name = options.load.split('.')[1]
    # Google sheet name if exist
    elif options.target.find('!') > 0 and not options.target.endswith('!'):
        name = options.target.split('!')[1]
    # MS graph sheet name if exist
    elif options.target.find('.xlsx:') > 0 and not options.target.endswith('.xlsx:'):
        name = options.target.rsplit(':')[1]
    # Exact target file names like test.csv
    elif options.target.find('.') > 0:
        name = options.target.split('.')[0]
    # Sql file name if single set
    elif options.extract:
        if options.extract.endswith('.sql'):
            name = options.extract.split('.')[0]
    elif options.source.find('!') > 0:
        name = options.source.split('!')[1]
    # Exact target file names from source
    elif source.find('.') > 0:
        name = source.split('.')[0]

    if len(source_list) > 1 and source in config.get('databases'):
        name = name + '-' + source
    return name


def get_queries():
    all_queries = find_all_files('sql')
    if options.extract:
        result = {options.extract: all_queries.get(options.extract)}
    elif options.execute:
        result = {options.execute: all_queries.get(options.execute)}
    else:
        # If option extract or execute is ommited,
        # then will run all queries for extraction
        result = {k: v for k, v in all_queries.items()
                  if str(v).endswith('.sql')}
    return result


def check_options():
    if options.extract and options.execute:
        logging.error("Options --extract and --execute are mutually exclusive")
        sys.exit(1)
    if options.source.endswith('!'):
        logging.error(
            f"--source {options.source} workbook_name without sheet_name")
        sys.exit(1)
    if options.source == 'csv': # ? это можно сделать в коллбеке
        if not os.path.exists(csv_dir):
            logging.error("Error: csv folder not found")
            sys.exit(1)
    if options.source == 'xls':
        if not os.path.exists(xls_dir):
            logging.error("Error: xls folder not found")
            sys.exit(1)


def get_sources():
    sources = ''
    if options.source == 'csv':
        sources = [s for s in os.listdir(csv_dir) if s.endswith('.csv')]
    elif options.source == 'xls':
        sources = ([
            s for s in os.listdir(xls_dir)
            if s.endswith('.xlsx') or s.endswith('.xls')
        ])
    elif options.source:
        sources = options.source.split(',')
    return sources


def find_all_files(extention):
    all_files = []
    for root, dirs, files in os.walk(options.dir, topdown=False):
        for name in files:
            if name.endswith(extention):
                all_files.append(os.path.join(root, name))
    return {os.path.basename(q): q for q in all_files}


def find_file(path, ends_mask, deep=False):
    """Find first file by endings with mask

    """
    if not os.path.exists(path):
        logging.error(f'{path} path not found')
    elif deep:
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(ends_mask):
                    return os.path.join(root, f)
    else:
        for f in os.listdir(path):
            if f.endswith(ends_mask):
                return os.path.join(path, f)


def get_config():
    """
    Detect and get etl config

    """
    home_path = os.path.expanduser('~')
    home_config_file = find_file(home_path, 'etl.yml')

    env_config_path = os.environ.get("ETL_CONFIG")
    env_config_path = '' if not env_config_path else env_config_path
    env_config_path = os.path.expanduser(env_config_path)

    # Command line option if set
    if os.path.exists(options.config_path):
        config_path = options.config_path
        logging.debug(f'Сonfig {config_path} found from option')

    # Path to config file in environment
    elif os.path.exists(env_config_path):
        config_path = env_config_path
        logging.debug(f'Сonfig {config_path} found from environment')

    # Config file in home directory
    elif home_config_file:
        config_path = home_config_file
        logging.debug(f'Сonfig {config_path} found from home')

    # If no config, creating base config by default
    else:
        home_config_file = os.path.join(home_path, '.etl.yml')
        with open(home_config_file, 'w+') as config_file:
            template = ("databases:\n"
                        "    local: 'sqlite:///local.db'\n"
                        "    alias1: "
                        "'postgres://user:pass@host:port/database'\n"
                        "    alias2: "
                        "'mysql+pymysql://user:pass@host:port/database"
                        "?charset=utf8'\n"
                        "\n"
                        "#gsheet_key: '~/.gsheets-credentials.json'")
            config_file.write(template)
        logging.info(f"New configuration file {home_config_file} was created")
        config_path = home_config_file

    with open(config_path, 'r') as config_file:
        cfg = yaml.safe_load(config_file)
    return cfg


def main():
    target_type = define_source_type(options.target)
    logging.debug(f'target type: {target_type} detected')
    target_method_list = {
        'csv': csv_load,
        'gsheet': gsheet_load,
        'msgraph': msgraph_load,
        'xls': xls_load,
        'database': database_load
    }
    target_method = target_method_list[target_type]

    for source in source_list:
        source_type = define_source_type(source)
        target_name = define_target_name(source)

        if source_type == 'database':
            # For saving data from multi source list with different names
            # we need add suffix to data_block name
            suffix = '' if len(source_list) == 1 else '-' + source
            if options.execute:
                sql_path = query_dict.get(options.execute)
                if sql_path:
                    sql = get_query(sql_path)
                    if unknown_options:
                        sql = str(sql).format(**unknown_options) # ok
                    logging.info(f'Executing: {sql_path}')
                    database_execute(sql=sql, db_name=source)
                else:
                    logging.error(f'Error: query {options.execute} not found')
            else:
                for query in query_dict:
                    # Use sql query name as name for
                    # outputs (files, sheet, tables)
                    target_name = query.split('.')[0] + suffix
                    sql_path = query_dict.get(query)
                    if sql_path:
                        sql = get_query(sql_path)
                        if unknown_options:
                            sql = str(sql).format(**unknown_options) # ok
                        logging.info(f'Getting data from {source} ' + \
                                     f'database with {sql_path}')
                        data = database_extract(sql=sql, db_name=source)
                        target_method(data_block_name=target_name, data=data)
                    else:
                        logging.error(f'Error: query {query} not found')

        if source_type == 'gsheet':
            workbook_name = source.split('!')[0]
            sheet_name = source.split('!')[1]
            logging.info(f'Getting data from {workbook_name}!{sheet_name} gsheet')
            data = gsheet_extract(workbook=workbook_name, sheet=sheet_name)
            target_method(data_block_name=target_name, data=data)

        if source_type == 'csv':
            logging.info(f'Getting data from {source} file')
            data = csv_extract(file_name=source)
            target_method(data_block_name=target_name, data=data)

        if source_type == 'xls':
            logging.info(f'Getting data from {source} file:')
            data = xls_extract(file_name=source)
            target_method(data_block_name=target_name, data=data)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click.pass_context
@click.option('--source', required=True,
              help="Source for extracting data. Database name, csv \
              or xls filename")
@click.option('--extract', default=False,
              help="Sql file name for extracting data from database")
@click.option('--execute', default=False,
            help="Sql file name for executing without extracting data")
@click.option('--target', default='csv',
              help="Target for inserting data. Database name, csv \
              or xls filename")
@click.option('--load', default=False,
              help="Database schema and table name, if target is database")
@click.option('--dir', default=os.getcwd(), show_default=True,
              help="Working directory for scripts,outputs,etc")
@click.option('--config-path', default='',
              help="Custom path to etl.yml config")
@click.option('--google_api_key', default='',
              help="Custom path to google-api-key.json config")
@click.option('--msgraph_api_key', default='',
              help="Custom path to microsoft-graph-api-key.yml config")
@click.option('--debug', default=False, is_flag=True,
              help="Extended level of logging with more info")
def cli(ctx, **kwargs):
    global options
    global unknown_options
    global config
    global source_list
    global query_dict
    global xls_dir
    global csv_dir


    options = type('OptionValuesClass', (), ctx.params)

    # Set directory to input/output
    xls_dir = os.path.join(options.dir, 'xls') + os.path.sep
    csv_dir = os.path.join(options.dir, 'csv') + os.path.sep

    check_options()

    # Setup logging params
    format = '%(asctime)s - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    if options.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
        logging.getLogger("googleapiclient").setLevel(logging.WARNING)
        logging.getLogger("oauth2client").setLevel(logging.WARNING)
    logging.basicConfig(level=logging_level, format=format, datefmt=datefmt, )

    unknown_options = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}
    if unknown_options:
        logging.debug(f'Unknown user options: {unknown_options}')

    # Read all queries, getting sources
    query_dict = get_queries()
    source_list = get_sources()

    # Getting config with databases conn strings
    config = get_config()

    # Main logic
    main()


if __name__ == "__main__":
    cli()
