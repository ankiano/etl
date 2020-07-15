#!/usr/bin/env python3.5
# coding=utf-8

import sys
import os
import logging
from optparse import OptionParser
import pandas as pd
import humanize
import pygsheets
import sqlalchemy
import yaml
import random


def get_query(sql_file_path):
    try:
        sql_file_path = sql_file_path.replace("\r", "")
        sql = open(sql_file_path, 'r', encoding='utf-8')
        result = " ".join(sql.readlines())
        return sqlalchemy.text(result)
    except Exception as e:
        logging.error('Error with reading query, %s', type(e))


def dataframe_size_info_msg(df):
    assert isinstance(df, pd.DataFrame), type(df)
    msg = '{} of data in {} cells obtained'.\
        format(humanize.naturalsize(
            df.memory_usage(index=True).sum()), df.size)
    return msg


def database_extract(**kwargs):
    sql = kwargs.get('sql')
    db_name = kwargs.get('db_name')
    engine = sqlalchemy.create_engine(config.get('databases').get(db_name))
    result = pd.read_sql(sql=sql, con=engine)
    logging.info(dataframe_size_info_msg(result))
    return result


def database_execute(**kwargs):
    sql = kwargs.get('sql')
    db_name = kwargs.get('db_name')
    engine = sqlalchemy.create_engine(config.get('databases').get(db_name))
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

    engine = sqlalchemy.create_engine(config.get('databases').get(db_name))

    data.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False,
        schema=schema_name
    )
    logging.info("Saved data to '{}.{}' table".
                 format(schema_name, table_name))


def csv_extract(**kwargs):
    file_name = kwargs.get('file_name')
    source_file_path = csv_dir + file_name
    result = pd.read_csv(source_file_path, header=0, sep=';')
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
    logging.info('Saved data to {}'.format(result_file_path))


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
        result_file_path = xls_dir + options.target.split('.')[0] \
                           + '.xlsx'
    writer = pd.ExcelWriter(result_file_path)
    data.to_excel(writer, sheet_name=data_block_name, index=False,
                  engine='xlsxwriter')
    writer.save()
    logging.info('Saved data to {}'.format(result_file_path))


def spreadsheet_open(workbook_name):
    """
    Authorize google client and open spreadsheet

    """

    # command option --google_api_key
    if os.path.isfile(options.google_api_key):
        key_path = options.google_api_key
        logging.debug('Google api key {} found '
                      'from command option --google_api_key'.\
                      format(os.path.abspath(key_path)))
    elif (config.get('google_api_keys')
        and options.google_api_key in config.get('google_api_keys').keys()):
        key_path = config.get('google_api_keys')[options.google_api_key]
        logging.debug('Google api key {} found '
                      'from etl.yml config file by alias={} '
                      'in command option --google_api_key'.\
                      format(os.path.abspath(key_path),options.google_api_key))
    # os evironment variable GOOGLE_API_KEY
    elif (os.environ.get("GOOGLE_API_KEY")
        and os.path.isfile(os.environ.get("GOOGLE_API_KEY"))):
        key_path = os.environ.get("GOOGLE_API_KEY")
        logging.debug('Google api key {} found '
                      'from os evironment variable GOOGLE_API_KEY'.\
                      format(os.path.abspath(key_path)))
    # randomly config (etl.yml) google_api_keys:
    elif config.get('google_api_keys'):
        key_path = random.choice(list(config.get('google_api_keys').values()))
        logging.debug('Google api key {} was taken randomly '
                      'from etl.yml config file (google_api_keys:)'.\
                      format(os.path.abspath(key_path)))
    # from user home dir
    elif os.path.isfile(os.path.expanduser('~/.google-api-key.json')):
        key_path = os.path.expanduser('~/.google-api-key.json')
        logging.debug('Google api key {} found '
                      'from user home dir'.format(os.path.abspath(key_path)))
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
        logging.error('Share spreadsheet {} with service email'.
                      format(workbook_name))
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
        logging.info('New sheet %s added ' % sheet_name)

    sheet.set_dataframe(data, start="A1", fit=True, nan='')
    logging.info('Saved data to {}!{} spreadsheet'.
                 format(workbook_name, sheet_name))


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
    elif source.endswith('.xls') or source.endswith('.xlsx'):
        return 'xls'
    elif source == 'csv':
        return 'csv'
    elif source == 'xls':
        return 'xls'
    elif source.find('!') > 0:
        return 'gsheet'
    else:
        logging.error('Data source (%s) is not recognized', source)
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
    # Exact target file names like test.csv
    elif options.target.find('.') > 0:
        name = options.target.split('.')[0]
    # Sheet name if exist
    elif options.target.find('!') > 0 and not options.target.endswith('!'):
        name = options.target.split('!')[1]
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
    if not options.source:
        parser.error('Error: Source not given')
    if options.extract and options.execute:
        parser.error("Options --extract and --execute are mutually exclusive")
    if options.source.endswith('!'):
        parser.error(
            "Error: options --source set workbook_name without sheet_name"
        )
    if options.source == 'csv':
        if not os.path.exists(csv_dir):
            parser.error("Error: csv folder not found")
    if options.source == 'xls':
        if not os.path.exists(xls_dir):
            parser.error("Error: xls folder not found")


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
        logging.error('{} path not found'.format(path))
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
    if os.path.exists(options.config):
        config_path = options.config
        logging.debug('Сonfig {} found from option'.format(config_path))

    # Path to config file in environment
    elif os.path.exists(env_config_path):
        config_path = env_config_path
        logging.debug('Сonfig {} found from environment'.format(config_path))

    # Config file in home directory
    elif home_config_file:
        config_path = home_config_file
        logging.debug('Сonfig {} found from home'.format(config_path))

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
        logging.info("New configuration file {} was created".
                     format(home_config_file))
        config_path = home_config_file

    with open(config_path, 'r') as config_file:
        cfg = yaml.safe_load(config_file)
    return cfg


def main():
    target_type = define_source_type(options.target)
    target_method_list = {
        'csv': csv_load,
        'gsheet': gsheet_load,
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
                    logging.info('Executing: {}'.format(sql_path))
                    database_execute(sql=sql, db_name=source)
                else:
                    logging.error('Error: query {} not found'.
                                  format(options.execute))
            else:
                for query in query_dict:
                    # Use sql query name as name for
                    # outputs (files, sheet, tables)
                    target_name = query.split('.')[0] + suffix
                    sql_path = query_dict.get(query)
                    if sql_path:
                        sql = get_query(sql_path)
                        logging.info('Getting data from {} database with {}'.
                                     format(source, sql_path))
                        data = database_extract(sql=sql, db_name=source)
                        target_method(data_block_name=target_name, data=data)
                    else:
                        logging.error('Error: query {} not found'.
                                      format(query))

        if source_type == 'gsheet':
            workbook_name = source.split('!')[0]
            sheet_name = source.split('!')[1]
            logging.info('Getting data from {}!{} gsheet'.
                         format(workbook_name, sheet_name))
            data = gsheet_extract(workbook=workbook_name, sheet=sheet_name)
            target_method(data_block_name=target_name, data=data)

        if source_type == 'csv':
            logging.info('Getting data from {} file'.format(source))
            data = csv_extract(file_name=source)
            target_method(data_block_name=target_name, data=data)

        if source_type == 'xls':
            logging.info('Getting data from {} file:'.format(source))
            data = xls_extract(file_name=source)
            target_method(data_block_name=target_name, data=data)


def define_options():
    parser.add_option(
        '--source',
        dest="source",
        default=False,
        help="Source for extracting data. Database name, csv or xls filename",
    )
    parser.add_option('--extract',
                      dest="extract",
                      default=False,
                      help="Source sql for extracting data from database")
    parser.add_option('--execute',
                      dest="execute",
                      default=False,
                      help="Sql file name for executing without "
                           "extracting data")
    parser.add_option('--target',
                      dest="target",
                      default='csv',
                      help="Target for inserting data. Database name, "
                           "csv or xls filename")
    parser.add_option('--load',
                      dest="load",
                      default=False,
                      help="Target for inserting data. Database _name, "
                           "csv or xls filename")
    parser.add_option('--dir',
                      dest="dir",
                      default=os.getcwd(),
                      help="Working directory for scripts,outputs,etc")
    parser.add_option('--config',
                      dest='config',
                      default='',
                      help="Custom path to etl.yml config")
    parser.add_option('--google_api_key',
                      dest='google_api_key',
                      default='',
                      help="Custom path to google-api-key.json config")
    parser.add_option('--debug',
                      action='store_true',
                      dest='debug',
                      default=False,
                      help="Extended level of logging with more info")


def run_console():
    global parser
    global options
    global source_list
    global query_dict
    global xls_dir
    global csv_dir
    global config

    # Getting parameters from command line
    parser = OptionParser()
    define_options()
    (options, args) = parser.parse_args()

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

    # Read all queries, getting sources
    query_dict = get_queries()
    source_list = get_sources()

    # Getting config with databases conn strings
    config = get_config()

    # Main logic
    main()


if __name__ == "__main__":
    run_console()
