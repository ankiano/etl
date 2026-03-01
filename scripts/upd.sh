#!/usr/bin/env bash
# upd — run update.sh (or any .sh file) with logging; create update.sh via TUI if absent

set -euo pipefail

# ─── helpers ────────────────────────────────────────────────────────────────

run_script() {
    local script="$1"
    local logfile="${script%.sh}.log"
#    echo "▶  Running $script (log → $logfile)"
    bash "$script" 2>&1 | tee "$logfile"
}

# ─── template definitions ───────────────────────────────────────────────────

tpl_blank() {
cat << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# add your etl commands here, for example:
# etl --source mydb --extract query.sql --target output/result.xlsx
EOF
}

tpl_adhoc() {
cat << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# [ -f local.db ] && rm local.db && echo "$(date "+%Y-%m-%d %H:%M:%S") | INFO  | $$ | local.db removed"
# etl --source input/data.xlsx --target local --load main.data
# etl --source local --extract result.sql --target output/result.xlsx
EOF
}

tpl_datafeed() {
cat << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# workbook='your-google-sheet-name'
# etl --source database --extract query1.sql --target gsheet --load "$workbook!sheet1" &
# etl --source database --extract query2.sql --target gsheet --load "$workbook!sheet2" &
# wait

# alternative: load to SharePoint / OneDrive Excel
# workbook='sites/YOUR-SITE-ID/drive/root:/report.xlsx:'
# etl --source database --extract query.sql --target sharepoint --load "$workbook??sheet_name=data"
EOF
}

tpl_datamart() {
cat << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# refresh fact table (partition replace)
# date_arg="${1:-$(date -v-1d +%F 2>/dev/null || date -d yesterday +%F)}"
# etl --source database2 --execute "alter table datamart.fact_table on cluster prod drop partition '$date_arg';"
# etl --source database1 --extract query_fact.sql --rep_date "$date_arg" \
#     --target database2 --load datamart.fact_table??chunksize=10000

# refresh dimension table (full reload)
# etl --source database2 --execute "truncate table datamart.dim_table on cluster prod;"
# etl --source database1 --extract query_dim.sql \
#     --target database2 --load datamart.dim_table??chunksize=10000
EOF
}

# ─── TUI: choose a template and create update.sh ────────────────────────────

create_update_sh() {
    echo ""
    echo "  update.sh not found in $(pwd)"
    echo "  choose a template to create it:"
    echo ""

    local options=("blank" "ad-hoc" "datafeed" "datamart" "cancel")
    local descriptions=(
        "empty stub with comments"
        "process local Excel/CSV files via DuckDB"
        "load DB data to Google Sheets / SharePoint Excel"
        "refresh fact + dimension tables (with date_arg)"
        "exit without creating"
    )

    PS3=$'\n  Your choice [1-5]: '
    select opt in "${options[@]}"; do
        case "$opt" in
            blank)    tpl_blank    > update.sh ;;
            ad-hoc)   tpl_adhoc   > update.sh ;;
            datafeed) tpl_datafeed > update.sh ;;
            datamart) tpl_datamart > update.sh ;;
            cancel)   echo "  Cancelled."; exit 0 ;;
            *)        echo "  Invalid choice, try again."; continue ;;
        esac

        chmod +x update.sh
        echo ""
        echo "$(date "+%Y-%m-%d %H:%M:%S") | INFO  | $$ | update.sh created (template: $opt)"
        echo "  open update.sh, edit it, then run: upd"
        break
    done
}

# ─── main ───────────────────────────────────────────────────────────────────

if [[ $# -eq 0 ]]; then
    # no arguments — run update.sh or create it
    if [[ -f update.sh ]]; then
        run_script update.sh
    else
        create_update_sh
    fi
elif [[ "$1" == *.sh ]]; then
    # explicit script name passed
    if [[ -f "$1" ]]; then
        run_script "$1"
    else
        echo "Error: file not found: $1" >&2
        exit 1
    fi
else
    echo "Usage: upd [script.sh]" >&2
    echo "  upd              — run update.sh (or create it via TUI if absent)" >&2
    echo "  upd my_script.sh — run my_script.sh, log to my_script.log" >&2
    exit 1
fi