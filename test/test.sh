script_dir=$(dirname $(readlink -f $0))
parent_dir=$(dirname $script_dir)

#python3 $parent_dir/etl/etl.py --source random-data.csv --target local --load main.product #--debug

#python3 $parent_dir/etl/etl.py --source local --extract color-cube.sql --target demo-datafeed! --debug

#python3 $parent_dir/etl/etl.py --source local --extract color-cube.sql --target demo-datafeed! --debug --google_api_key ~/tmp/config/.gsheets-credentials.json

python3 $parent_dir/etl/etl.py --source local --extract color-cube.sql --target demo-datafeed! --debug --google_api_key key2

#python3 $parent_dir/etl/etl.py --source local --target xls

#python3 $parent_dir/etl/etl.py --source csv --target xls

