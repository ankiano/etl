#!/usr/bin/env python3.10
# coding=utf-8

import os, sys
import logging
import click as cli # command line interface
import pandas as pd
import sqlalchemy
import yaml
import humanize
from urllib.parse import urlparse
from urllib.parse import parse_qs
import random
import numpy as np
import urllib
import json

special_sources = ['http://','https://','ftp://','google+sheets', 'microsoft+graph']

def parse_url_params(url):
    result = dict()
    x = url.split("&")
    for i in x:
        a,b=i.split("=")
        result[a]=b
    return result

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

def api_call(method, url, body=None, **kwargs):
    resource = kwargs.get('resource', None)
    access_token = kwargs.get('access_token', None)
    http_headers = {'Authorization':  access_token,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'}
    endpoint = urllib.parse.urljoin(resource,url.lstrip('/'))
    logging.debug(f'endpoint: {endpoint}')
    return method(endpoint, headers=http_headers, json=body)


def spreadsheet_open(workbook_name, credentials_path):
    """
    Authorize google client and open spreadsheet

    """
    pygsheets = __import__('pygsheets')
    # command option --google_api_key
    credentials_path = os.path.expanduser(credentials_path)
    if os.path.isfile(credentials_path):
        log.debug(f'google api key found <{credentials_path}>')
    else:
        log.error(f'google api key file not found <{credentials_path}>')
        sys.exit(1)

    # To prevent email printing by pygsheets
    sys.stdout = open(os.devnull, "w")
    try:
        gclient = pygsheets.authorize(service_file=credentials_path)
    except Exception as e:
        log.error(e)
        sys.exit(1)
    # Switch to normal
    sys.stdout = sys.__stdout__
    try:
        workbook = gclient.open(workbook_name)
    except pygsheets.exceptions.SpreadsheetNotFound:
        log.error(f'SpreadsheetNotFound: share spreadsheet <{workbook_name}> with service email')
        sys.exit(1)
    except Exception as e:
        log.error(e)
        sys.exit(1)
    return workbook

def msgraph_open(credentials_path):
    """
    Authorize microsoft graph api client and get token

    """
    msal = __import__('msal')
    # command option --msgraph_api_key
    credentials_path = os.path.expanduser(credentials_path)
    if os.path.isfile(credentials_path):
        log.debug(f'graph api key found <{credentials_path}>')
    else:
        log.error(f'graph api key file not found <{credentials_path}>')
        sys.exit(1)

    # read config from yaml file
    with open(credentials_path, 'r') as config_file:
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
        logging.error('microsoft graph api error: {}'.
                      format(token_response['error_description']))
        sys.exit(1)
    return token_response,cfg

def get_source(source):
    if '://' in source:
        result = source
        log.debug(f'source defined like a connection string <{source}>')
    else:
        cfg = get_config(source)
        if cfg.get(source):
            s = cfg.get(source)
            if isinstance(s, list):
                result = random.choice(s)
                log.debug(f"source defined like a random choice by alias <{source}>")
            else:
                result = s
                log.debug(f'source defined by alias from config file <{source}>')
        else:
            if '.' in source:
                log.error(f'file name not found <{source}>')
            else:
                log.error(f'source alias not found <{source}>')
            sys.exit(1)
    return result

def dataframe_size_info(df):
    assert isinstance(df, pd.DataFrame), type(df)
    # Check if the DataFrame is empty and handle accordingly
    if df.empty:
        memory_usage = 0  # Set to zero if the DataFrame is empty
    else:
        memory_usage = df.memory_usage(index=True).sum()
    # Only apply humanize if there's memory usage; otherwise, set to "0 B" or an appropriate default
    volume = humanize.naturalsize(memory_usage, binary=True) if memory_usage > 0 else "0 B"
    return f'{volume} of data received in amount of {df.shape[0]} rows, {df.shape[1]} columns, {df.size} cells'

def get_config(alias):
    """
    Detect and get etl config

    """
    home_config_file =  os.path.expanduser('~/.etl.yml')

    env_config_path = os.environ.get("ETL_CONFIG")
    env_config_path = '' if not env_config_path else env_config_path
    env_config_path = os.path.expanduser(env_config_path)

    # Command line option if set
    if os.path.exists(options.config_path):
        config_path = options.config_path
        log.debug(f'config file found from command option <{config_path}>')

    # Path to config file in environment
    elif os.path.exists(env_config_path):
        config_path = env_config_path
        log.debug(f'config file found from environment <{config_path}>')

    # Config file in home directory
    elif os.path.exists(home_config_file):
        config_path = home_config_file
        log.debug(f'config file found from home dir <{config_path}>')
    else:
        log.error(f'config file not found, alias not possible to recognize <{alias}>')
        sys.exit(1)

    with open(config_path, 'r') as config_file:
        cfg = yaml.safe_load(config_file)
        # log.debug(f'config contains: {cfg}')
    return cfg

def get_query(query, extra_args):
    try:
        if query.endswith('.sql'):
            if os.path.isfile(query):
                sql_file_path = query.replace("\r", "")
                sql = open(sql_file_path, 'r', encoding='utf-8')
                result = " ".join(sql.readlines())
            else:
                log.error(f'query file not found <{query}>')
                sys.exit(1)
        else:
            result = query
        if extra_args:
            result = str(result).format(**extra_args) 
        result = sqlalchemy.text(result)
        log.debug(f'sql:\n{result}')
        return result
    except Exception as e:
        log.error(e)

def create_dir(path):
    # manage folders if not exist
    dir = os.path.dirname(path)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
        log.info(f'folder created <{dir}>')

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@cli.pass_context
@cli.option('--source', required=True, type=str, help="Source for extracting data. Database name, csv or xls filename")
@cli.option('--extract', default='', help="Sql file name for extracting data from database")
@cli.option('--execute', default='', help="Sql file name for executing without extracting data")
@cli.option('--target', help="Target for inserting data. Database name, csv or xls filename")
@cli.option('--load', default='', help="Database schema and table name, if target is database")
@cli.option('--config-path', default='', help="Custom path to etl.yml config")
@cli.option('--debug', default=False, is_flag=True, help="Extended level of logging with more info")
def cli(ctx, **kwargs):
    global log
    global options
    global extra_args
# logging basic setup
    log_level = logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s | %(levelname)-5s | %(process)d | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger()

# read cli options and extra args
    try:
        options = type('OptionValuesClass', (), ctx.params)
        extra_args = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}
    # except TypeError:
        # sys.exit(1) # only --help option rise typeError: cannot unpack non-iterable int object
    except Exception as e:
        log.error(e)
        sys.exit(1)
    if options.debug:
        log.setLevel(logging.DEBUG)

    log.debug(f'project dir <{os.getcwd()}>')

# print cli option in debug mode
    if options.debug:
        option_list = [option for option in dir(options) if not option.startswith("__")]
        o = {}
        for i in option_list:
            value = getattr(options,i)
            if value:
                o[i] = getattr(options,i)
        log.debug(f'command options: {o}')
        if extra_args:
            log.debug(f'custom params for query: {extra_args}')
    else:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# check options
    if options.extract and options.execute:
        log.error("options --extract and --execute are mutually exclusive")
        sys.exit(1)

# extract dataset from source
    dataset = pd.DataFrame()
    if options.source:
        source_params = {}
        if '??' in options.source: # take parameters for sqlalchemy engine
            source, source_params = options.source.split('??')
            source_params = parse_url_params(source_params)
        else: # parameters after ? will be forwarded directry to source/target
            source = options.source

        if os.path.isfile(source): # file
            log.debug(f'source params: {source_params}')
            if source.endswith('.csv'):
                source_params.setdefault('header',0) # default params # means you have the names of columns in the first row in the file
                source_params.setdefault('sep',';') # default params
                source_method = pd.read_csv
            if source.endswith('.xlsx') or source.endswith('.xls'):
                source_params.setdefault('header',0) # default params
                source_params.setdefault('engine','openpyxl') # default params
                source_method = pd.read_excel
            if source.endswith('.parquet'):
                source_method = pd.read_parquet
            if source.endswith('.xml'):
                source_method = pd.read_xml
            if source.endswith('.json'):
                source_method = pd.read_json
            try:
                log.info(f'extracting data from <{source}>')
                dataset = source_method(source, **source_params)
            except Exception as e:
                log.error(e)
                sys.exit(1)
        # extract from sources with connection string
        else:
            source = get_source(options.source)
            if '??' in source: # take parameters for sqlalchemy engine
                source, source_params = source.split('??')
                source_params = parse_url_params(source_params)
                log.debug(f'source params: {source_params}')

            if any(s in source for s in special_sources): # any custom sources and apies
                # extract from google sheets
                if 'google+sheets' in source:
                    workbook = spreadsheet_open(options.extract.split('!')[0], source_params['credentials'])
                    sheet = workbook.worksheet_by_title(options.extract.split('!')[1])
                    dataset = sheet.get_as_df()
                if 'microsoft+graph' in source:
                    token_response, cfg = msgraph_open(source_params.get('credentials'))
                    log.debug(token_response)
                    workbook_url = options.extract
                    sheet_name = 'data'
                    if '??' in options.extract:
                        workbook_url, sheet_name = options.extract.split('??')
                        sheet_name = parse_url_params(sheet_name)
                        sheet_name = sheet_name.pop('sheet_name', 'data')
                    
                    requests = __import__('requests')
                    url = workbook_url + f"/workbook/worksheets/{sheet_name}/usedRange()"
                    response = api_call(requests.get, url, resource=cfg['resource'], access_token=token_response['access_token'])
                    response
                    data = response.json()['values']
                    dataset = pd.DataFrame(data[1:], columns = data[0])

                # extract csv from internent
                if any(s in source for s in ['http','https','ftp']) and source.endswith('.csv'):
                    log.info(f'extracting data from <{source}>')
                    source_params.setdefault('sep',';') # default params
                    source_params.setdefault('header',0) # default params # means you have the names of columns in the first row in the file
                    try:
                        dataset = pd.read_csv(source, **source_params)
                    except Exception as e:
                        log.error(e)
                        sys.exit(1)
            else:
                try:
                    source_params.setdefault('max_identifier_length',128) # default params
                    source_engine = sqlalchemy.create_engine(source, **source_params)
                    if options.execute:
                        log.info(f'executing <{options.execute}> on <{options.source}>')
                        source_query = get_query(options.execute, extra_args)
                        if sqlalchemy.__version__.startswith("2"):  # SQLAlchemy 2.0+
                            with source_engine.connect() as connection:
                                 connection.execute(source_query)
                        else: # SQLAlchemy < 2.0
                            source_engine.execute(source_query)
                        if extra_args:
                            log.info(f'executed <{options.execute}> with user_variables {extra_args}')
                        else:
                            log.info(f'executed <{options.execute}>')
                    if options.extract:
                        log.info(f'extracting data from <{options.source}> using query <{options.extract}>')
                        source_query = get_query(options.extract, extra_args)
                        dataset = pd.read_sql(sql=source_query, con=source_engine)
                except Exception as e:
                        log.error(e)
                        sys.exit(1)

    if not options.execute:
        log.info(dataframe_size_info(dataset))
    
    # check if dataset is empty
    if options.extract and dataset.empty:
        log.warning("no data received, exiting without updating target")
        return sys.exit(0)

    # load dataset to target
    if options.target:
        target_params = {}
        if '??' in options.target: # take parameters for sqlalchemy engine
            target, target_params = options.target.split('??')
        else: # parameters after ? will be forwarded directry to source/target
            target = options.target
        if target_params:
            target_params = parse_url_params(target_params)
        
        # load to csv
        if target.endswith('.csv'):
            create_dir(target) # manage folders if not exist
            target_params.setdefault('sep',';') # default params
            target_params.setdefault('encoding','utf-8')
            target_params.setdefault('index',False)
            try: # load data
                log.debug(f'target params: {target_params}')
                dataset.to_csv(target, **target_params)
                log.info(f'data saved to file <{target}>')
            except Exception as e:
                log.error(e)
        # load to xlsx
        elif target.endswith('.xlsx') or target.endswith('.xls'):
            create_dir(target) # manage folders if not exist
            target_params.setdefault('engine','openpyxl')
            target_params.setdefault('if_sheet_exists','replace')
            log.debug(f'target params: {target_params}')
            sheet_name = target_params.pop('sheet_name', 'data')
            if os.path.exists(target):
                mode = target_params.pop('mode', 'a') # read file mode or append by default
            else:    
                mode='w' #create new file mode
            if mode == 'w': #if_sheet_exists is valid only when append mode
                target_params.pop('if_sheet_exists', None)
            try: # load data
                with pd.ExcelWriter(target, mode=mode, **target_params) as writer:
                    dataset.to_excel(writer, sheet_name=sheet_name, index=False) 
                log.info(f'data saved to file <{target}> on sheet <{sheet_name}>')
            except Exception as e:
                log.error(e)
        # load to parquet
        elif target.endswith('.parquet'):
            create_dir(target) # manage folders if not exist
            target_params.setdefault('index',False)
            try: # load data
                dataset.to_parquet(target, **target_params)
                log.info(f'data saved to file <{target}>')
            except Exception as e:
                log.error(e)
        # load to xml
        elif target.endswith('.xml'):
            create_dir(target) # manage folders if not exist
            target_params.setdefault('index',False)
            try: # load data
                dataset.to_xml(target, **target_params)
                log.info(f'data saved to file <{target}>')
            except Exception as e:
                log.error(e)
        # load to html
        elif target.endswith('.html'):
            create_dir(target) # manage folders if not exist
            target_params.setdefault('index',False)
            try: # load data
                dataset.to_html(target, **target_params)
                log.info(f'data saved to file <{target}>')
            except Exception as e:
                log.error(e)
        # load to json
        elif target.endswith('.json'):
            create_dir(target) # manage folders if not exist
            target_params.setdefault('index',False)
            try: # load data
                dataset.to_json(target, **target_params)
                log.info(f'data saved to file <{target}>')
            except Exception as e:
                log.error(e)
        # load to sources with connection strings
        else:
            target = get_source(target) #target can be set like alias
            if '??' in target: # take parameters for sqlalchemy engine
                target, target_params = target.split('??')
            if target_params:
                target_params = parse_url_params(target_params)
            
            if any(s in target for s in special_sources): # any custom sources and apies
                log.debug(f'target params: {target_params}')
                # load to google sheets
                if 'google+sheets' in target:
                    if dataset.size <= 10000000:
                        workbook_name, sheet_name = options.load.split('!')
                        workbook = spreadsheet_open(workbook_name, target_params.get('credentials'))
                        google_err = __import__('pygsheets.exceptions')
                        try:
                            log.info(f'loading data to google speadsheet <{workbook_name}>')
                            sheet = workbook.worksheet_by_title(sheet_name)
                            sheet.clear(start='A1')
                        except google_err.WorksheetNotFound:
                            sheet = workbook.add_worksheet(sheet_name, rows=1, cols=1)
                            log.info(f'new sheet added <{sheet_name}>')
                        except Exception as e:
                            log.error(e)
                        
                        dataset = dataset.fillna('')
                        dataset = dataset.astype(str)
                        sheet.set_dataframe(dataset, start="A1", fit=True, nan='')
                        log.info(f'data saved to spreadsheet <{workbook_name}!{sheet_name}>')
                    else:
                        log.error('saving to gsheet is ommited due to limit 10M of cells')
                        sys.exit(1)
                if 'microsoft+graph' in target:
                    if dataset.size <= 5000000:
                        token_response, cfg = msgraph_open(target_params.get('credentials'))
                        log.debug(token_response)
                        urllib = __import__('urllib')
                        requests = __import__('requests')
                        # access_token = token_response['access_token']
                        
                        workbook_url = options.load
                        sheet_name = 'data'
                        if '??' in options.load:
                            workbook_url, sheet_name = options.load.split('??')
                            sheet_name = parse_url_params(sheet_name)
                            sheet_name = sheet_name.pop('sheet_name', 'data')
                        url = workbook_url + f"/workbook/worksheets"
                        # try to add worksheet
                        response = api_call(requests.post, url, {"name": f"{sheet_name}"}, resource=cfg['resource'], access_token=token_response['access_token'])
                        if response.status_code == 201:
                            logging.info(f'New sheet <{sheet_name}> added')
                        # clear all worksheet range
                        url = workbook_url + f"/workbook/worksheets/{sheet_name}/range(address='A:XFD')/clear"
                        response = api_call(requests.post, url, {"applyTo": "All"}, resource=cfg['resource'], access_token=token_response['access_token'])
                        logging.debug(response)
                        # add new table
                        url = workbook_url + f"/workbook/worksheets/{sheet_name}/tables/add"
                        col_range = 'A1:%s1' % colnum_string(len(dataset.columns))
                        response = api_call(requests.post, url, {"address": f"{col_range}","hasHeaders": True, "name": sheet_name}, resource=cfg['resource'], access_token=token_response['access_token']).json()
                        table_id = response.get('id')
                        if response.get('error'):
                            logging.error(f"{response['error']['code']}: {response['error']['message']}")
                            sys.exit(1)
                        # add table header
                        url = workbook_url + f"/workbook/worksheets/{sheet_name}/range(address='{col_range}')"
                        body = {'values': [dataset.to_dict(orient='split')['columns']]}
                        response = api_call(requests.patch, url, body, resource=cfg['resource'], access_token=token_response['access_token'])
                        dataset = dataset.fillna('')
                        # add rows by chanks
                        chunksize = 1000
                        for g, df in dataset.groupby(np.arange(len(dataset)) // chunksize):
                            url = workbook_url + f"/workbook/tables/{table_id}/Rows"
                            data_dictionary = df.to_dict(orient='split')['data']
                            data_body = json.dumps(data_dictionary, default=str) # to awoid TypeError: Object of type date is not JSON serializable
                            body={'values': json.loads(data_body)}
                            response = api_call(requests.post, url, body, resource=cfg['resource'], access_token=token_response['access_token'])
                        if response.status_code == 201:
                            logging.info(f'Saved data to <{workbook_url}> on <{sheet_name}> sheet')
                    else:
                        log.error('saving to graph api is ommited due to limit 5M of cells')
                        sys.exit(1)
            # any sql sources supported by sqlalchemy or its extentions
            else: 
                target_params.setdefault('max_identifier_length', 128) # default params
                engine = sqlalchemy.create_engine(target, **target_params)
                
                @sqlalchemy.event.listens_for(engine, "do_setinputsizes")
                # The CLOB datatype in cx_Oracle incurs a significant performance overhead
                def _remove_clob(inputsizes, cursor, statement, parameters, context):
                    for bindparam, dbapitype in list(inputsizes.items()):
                        if dbapitype is sqlalchemy.CLOB:
                            del inputsizes[bindparam]

                if options.load:
                    load_params = {}
                    load = options.load
                    if '??' in load: # take parameters for loading data
                        load, load_params = load.split('??')
                    if load_params:
                        load_params = parse_url_params(load_params)
                    load_params.setdefault('if_exists','append')
                    if load_params.get('index'):
                        load_params['index'] = bool(load_params['index'].lower() == 'true')
                    else:
                        load_params.setdefault('index',False)
                    if load_params.get('chunksize'):
                        load_params['chunksize'] = int(load_params['chunksize'])     
                    log.debug(f'load params: {load_params}')
                    if '.' in load:
                        schema, table  = load.split('.')
                    else:
                        table = load
                        schema = None
                    try:
                        dataset.to_sql(name=table, schema=schema, con=engine, **load_params)
                        log.info(f'data saved to <{options.target}> in table <{options.load}>')
                    except Exception as e:
                        log.error(e)


if __name__ == "__main__":
    cli()
