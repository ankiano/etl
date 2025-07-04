script_dir=$(dirname $(readlink -f $0))
parent_dir=$(dirname $script_dir)


#python3 $parent_dir/etl.py --help

#python3 $parent_dir/etl.py --source 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv??sep=,' > titanic.csv

#python3 $parent_dir/etl.py --source 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv??sep=,' \
#                           --target 'input/titanic.xlsx??sheet_name=2&if_sheet_exists=replace' --debug

#python3 $parent_dir/etl.py --source 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv??sep=,' \
#                           --target local --load 'main.titanic'

#python3 $parent_dir/etl.py --source input/titanic.csv \
#                           --target 'sqlite:///local.db' --load main.titanic

#python3 $parent_dir/etl.py --source local \
#                           --execute  'drop table {table_name}' --table_name titanic

#python3 $parent_dir/etl.py --source input/titanic.csv \
#                           --target local \
#                           --load main.titanic

#python3 $parent_dir/etl.py --source input/titanic.csv \
#                           --target output/titanic.xls \
#                           --debug

#python3 $parent_dir/etl.py --source input/titanic.csv \
#                           --target 'output/titanic.xlsx??sheet_name=data' \
#                           --debug

#python3 $parent_dir/etl.py --source input/titanic.csv \
#                           --target output/titanic.xml \
#                           --debug

#python3 $parent_dir/etl.py --source input/titanic.csv \
#                           --target output/titanic.parquet \
#                           --debug

#python3 $parent_dir/etl.py --source output/titanic.xls \
#                           --target local \
#                           --load main.test_xls \
#                           --debug

#python3 $parent_dir/etl.py --source output/titanic.xlsx \
#                           --target local \
#                           --load test_xlsx \
#                           --debug

#python3 $parent_dir/etl.py --source output/titanic.xml \
#                           --target local \
#                           --load test_xml \
#                           --debug

#python3 $parent_dir/etl.py --source output/titanic.parquet \
#                           --target local \
#                           --load test_parquet \
#                           --debug

#python3 $parent_dir/etl.py --source local \
#                           --extract 'select * from test_{table_name}' \
#                           --table_name 'xls' \
#                           --target 'google+sheets:///??credentials=~/.google-api-key.json' \
#                           --load test-datafeed!titanic \
#                           --debug

#python3 $parent_dir/etl.py --source local \
#                           --extract sql/age.sql \
#                           --target gsheets \
#                           --load test-datafeed!age \
#                           --debug

#python3 $parent_dir/etl.py --source local \
#                           --extract sql/age.sql \
#                           --target output/age.csv

#python3 $parent_dir/etl.py --source input/titanic.xlsx \
#                           --target sharepoint \
#                           --load "/users/jonh.do@domain.com/drive/root:/Book.xlsx:??sheet_name=data" \
#                           --debug

#python3 $parent_dir/etl.py --source sharepoint \
#                           --extract "/users/john.do@domain.com/drive/root:/Book.xlsx:??sheet_name=data" \
#                           --target output/test.csv \
#                           --debug

#python3 $parent_dir/etl.py --source local --extract 'select * from main.titanic' --target output/titanic.xlsx

#cat titanic.csv | python3 $parent_dir/etl.py --target 'input/titanic.xlsx??sheet_name=2&if_sheet_exists=replace'

#cat titanic.csv | python3 $parent_dir/etl.py > test.csv

#cat titanic.csv | python3 $parent_dir/etl.py | cat

#cat titanic.csv | python3 $parent_dir/etl.py | wc -l

#cat titanic.csv | python3 $parent_dir/etl.py | grep female | wc -l

#cat titanic.csv | python3 $parent_dir/etl.py --target local --load main.titanic

#python3 $parent_dir/etl.py --source local --execute "truncate table main.titanic"
