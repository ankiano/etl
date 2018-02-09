script_dir=$(dirname $(readlink -f $0))
parent_dir=$(dirname $script_dir)

python3 $parent_dir/etl/etl.py --source random-data.csv --target local --load main.product #--debug

python3 $parent_dir/etl/etl.py --source local --extract color-cube.sql --target demodatafeed! #--debug

python3 $parent_dir/etl/etl.py --source local --target xls
