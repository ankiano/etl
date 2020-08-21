script_dir=$(dirname $(readlink -f $0))
parent_dir=$(dirname $script_dir)


python3 $parent_dir/etl.py --help

#python3 $parent_dir/etl.py --source random-data.csv --target local --load main.product
#python3 $parent_dir/etl.py --source local --extract color-cube.sql --target xls
#python3 $parent_dir/etl.py --source local --target xls
#python3 $parent_dir/etl.py --source csv --target xls


# using google key from custom path
#python3 $parent_dir/etl.py --source local --extract color-cube.sql --target demo-datafeed! \
#                           --debug --google_api_key ~/tmp/config/.test-key.json
# using google key by alias in config file
#python3 $parent_dir/etl.py --source local --extract color-cube.sql --target demo-datafeed! \
#                           --debug --google_api_key key2


#errors check
#python3 $parent_dir/etl.py --target xls
#python3 $parent_dir/etl.py --source demo-datafeed!