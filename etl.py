#!/usr/bin/env python3.9
# coding=utf-8

import os, sys
import logging
import click as cli # command line interface
# import pdb #debug
import pandas as pd
import sqlalchemy
import yaml
import humanize
from urllib.parse import urlparse
from urllib.parse import parse_qs
import random

special_sources = ['http','https','ftp','google+sheets']

def parse_url_params(url):
    result = dict()
    x = url.split("&")
    for i in x:
        a,b=i.split("=")
        result[a]=b
    return result

def spreadsheet_open(workbook_name, credentials_path):
    """
    Authorize google client and open spreadsheet

    """
    pygsheets = __import__('pygsheets')
    # command option --google_api_key
    credentials_path = os.path.expanduser(credentials_path)
    if os.path.isfile(credentials_path):
        log.debug(f'google api key {credentials_path} found')
    else:
        log.error(f'google api key file {credentials_path} not found.')
        sys.exit(1)

    # To prevent email printing by pygsheets
    sys.stdout = open(os.devnull, "w")
    try:
        gclient = pygsheets.authorize(service_file=credentials_path, no_cache=True, retries=3)
    except Exception as e:
        log.error(e)
        sys.exit(1)
    # Switch to normal
    sys.stdout = sys.__stdout__
    try:
        workbook = gclient.open(workbook_name)
    except pygsheets.exceptions.SpreadsheetNotFound:
        log.error(f'spreadsheetNotFound error. share spreadsheet {workbook_name} with service email')
        sys.exit(1)
    except Exception as e:
        log.error(e)
        sys.exit(1)
    return workbook

def get_source(source):
    if '://' in source:
        result = source
        log.debug(f'source defined like a connection string: {source}')
    else:
        cfg = get_config(source)
        if cfg.get(source):
            s = cfg.get(source)
            if isinstance(s, list):
                result = random.choice(s)
                log.debug(f"source defined like a random choice by alias <{source}> from config file")
            else:
                result = s
                log.debug(f'source defined by alias <{source}> from config file')
        else:
            if '.' in source:
                log.error(f'<{source}> file not found')
            else:
                log.error(f'alias <{source}> not found in config file')
            sys.exit(1)
    return result

def dataframe_size_info(df):
    assert isinstance(df, pd.DataFrame), type(df)
    volume = humanize.naturalsize(df.memory_usage(index=True).sum())
    return f'{volume} of data in amount of {df.shape[0]} rows,{df.shape[1]} columns,{df.size} cells recieved'

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
        log.debug(f'config file found from command option: {config_path}')

    # Path to config file in environment
    elif os.path.exists(env_config_path):
        config_path = env_config_path
        log.debug(f'config file found from environment: {config_path}')

    # Config file in home directory
    elif os.path.exists(home_config_file):
        config_path = home_config_file
        log.debug(f'config file found from home dir: {config_path}')
    else:
        log.error(f'alias <{alias}> not possible to recognize, config file not found')
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
                log.error(f'query file <{query}> not found. check query name and path.')
                sys.exit(1)
        else:
            result = query
        result = sqlalchemy.text(result)
        if extra_args:
            result = str(result).format(**extra_args) 
        log.debug(f'sql:\n{result}')
        return result
    except Exception as e:
        log.error(e)

def create_dir(path):
    # manage folders if not exist
    dir = os.path.dirname(path)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
        log.info(f'folder {dir} created')

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
    logging.basicConfig(level=log_level, format='%(asctime)s | %(levelname)-5s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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

    log.debug(f'project dir: {os.getcwd()}')

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
                source_params.setdefault('low_memory',False) # default params
                source_method = pd.read_csv
            if source.endswith('.xlsx') or source.endswith('.xls'):
                source_params.setdefault('header',0) # default params
                source_params.setdefault('engine','openpyxl') # default params
                source_method = pd.read_excel
            if source.endswith('.parquet'):
                source_method = pd.read_parquet
            if source.endswith('.xml'):
                source_method = pd.read_xml
            try:
                log.info(f'extracting data from {source}')
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
                # extract csv from internent
                if any(s in source for s in ['http','https','ftp']) and source.endswith('.csv'):
                    log.info(f'extracting data from {source}')
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
                        source_engine.execute(source_query)
                        if extra_args:
                            log.info(f'executed <{options.execute}> with user_variables {extra_args}')
                        else:
                            log.info(f'executed <{options.execute}>')
                    if options.extract:
                        log.info(f'extracting data from a <{options.source}> using query <{options.extract}>')
                        source_query = get_query(options.extract, extra_args)
                        dataset = pd.read_sql(sql=source_query, con=source_engine)
                except Exception as e:
                        log.error(e)
                        sys.exit(1)

#     dataset = dataset.dropna() #dropping all rows where are completely empty
    log.info(dataframe_size_info(dataset))

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
                log.info(f'data saved to file: {target}')
            except Exception as e:
                log.error(e)
        # load to xlsx
        elif target.endswith('.xlsx') or target.endswith('.xls'):
            create_dir(target) # manage folders if not exist
            target_params.setdefault('index',False)
            try: # load data
                dataset.to_excel(target, **target_params)
                log.info(f'data saved to file <{target}>')
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
        # load to sources with connection strings
        else:
            target = get_source(target) #target can be set like alias
            if '??' in target: # take parameters for sqlalchemy engine
                target, target_params = target.split('??')
            if target_params:
                target_params = parse_url_params(target_params)
            
            if any(s in target for s in special_sources): # any custom sources and apies
                # load to google sheets
                if 'google+sheets' in target:
                    if dataset.size <= 5000000:
                        log.debug(f'target params: {target_params}')
                        workbook_name, sheet_name = options.load.split('!')
                        workbook = spreadsheet_open(workbook_name, target_params.get('credentials'))
                        google_err = __import__('pygsheets.exceptions')
                        try:
                            log.info(f'loading data to google speadsheet <{workbook_name}>')
                            sheet = workbook.worksheet_by_title(sheet_name)
                            sheet.clear(start='A1')
                        except google_err.WorksheetNotFound:
                            sheet = workbook.add_worksheet(sheet_name, rows=1, cols=1)
                            log.info(f'new sheet <{sheet_name}> added')
                        except Exception as e:
                            log.error(e)
                        
                        dataset = dataset.fillna('')
                        dataset = dataset.astype(str)
                        sheet.set_dataframe(dataset, start="A1", fit=True, nan='')
                        log.info(f'data saved to <{workbook_name}!{sheet_name}> spreadsheet')
                    else:
                        log.error('saving to gsheet is ommited due to limit 5M of cells')
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
                    if '??' in options.load: # take parameters for loading data
                        load, load_params = options.load.split('??')
                    else:
                        load = options.load
                    if load_params:
                        load_params = parse_url_params(load_params)
                    load_params.setdefault('if_exists','append')
                    load_params.setdefault('index',False)
                    log.debug(f'load params: {load_params}')
                    if '.' in load:
                        schema, table  = options.load.split('.')
                    else:
                        table = options.load
                        schema = None
                    try:
                        dataset.to_sql(name=table, schema=schema, con=engine, **load_params)
                        log.info(f'saved data to <{target}> in <{load} table')
                    except Exception as e:
                        log.error(e)


if __name__ == "__main__":
    cli()
