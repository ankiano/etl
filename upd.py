def main():
    """Entry point for the `upd` CLI command.

    The bash script is embedded here to make the package self-contained —
    no package_data needed, works with pip and pipx.
    """
    import sys
    import os
    import tempfile
    import subprocess

    script = r"""#!/usr/bin/env bash
# upd — run update.sh (or any .sh file) with logging; create update.sh via TUI if absent

set -euo pipefail


# ─── template definitions ───────────────────────────────────────────────────

tpl_blank() {
cat << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

# etl --source mydb --extract query.sql --target result.csv
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

# load to google sheet
# workbook='your-google-sheet-name'
# etl --source database --extract query1.sql --target gsheet --load "$workbook!sheet1" &
# etl --source database --extract query2.sql --target gsheet --load "$workbook!sheet2" &
# wait

# load to sharepoint / onedrive excel
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

# ─── logging ────────────────────────────────────────────────────────────────

log_info()  { echo "$(date "+%Y-%m-%d %H:%M:%S") | INFO  | $$ | $*"; }
log_warn()  { echo "$(date "+%Y-%m-%d %H:%M:%S") | WARN  | $$ | $*" >&2; }
log_error() { echo "$(date "+%Y-%m-%d %H:%M:%S") | ERROR | $$ | $*" >&2; }

# ─── TUI: choose a template and create update.sh ────────────────────────────

create_update_sh() {
    log_warn "update.sh not found in $(pwd)"
    log_info "to create new update.sh - select a template:"

    local options=("blank" "ad-hoc" "datafeed" "datamart" "cancel")

    PS3=$'\n  Your choice [1-5]: '
    echo ""
    select opt in "${options[@]}"; do
        case "$opt" in
            blank)    tpl_blank     > update.sh ;;
            ad-hoc)   tpl_adhoc    > update.sh ;;
            datafeed) tpl_datafeed  > update.sh ;;
            datamart) tpl_datamart  > update.sh ;;
            cancel)   log_info "cancelled"; exit 0 ;;
            *)        log_warn "invalid choice, try again"; continue ;;
        esac

        chmod +x update.sh
        echo ""
        log_info "update.sh created (template: $opt)"
        log_info "open update.sh, edit it, then run: upd"
        break
    done
}

# ─── main ───────────────────────────────────────────────────────────────────

if [[ $# -eq 0 ]]; then
    if [[ -f update.sh ]]; then
        bash update.sh 2>&1 | tee update.log
    else
        create_update_sh
    fi
elif [[ "$1" == *.sh ]]; then
    if [[ -f "$1" ]]; then
        bash "$1" 2>&1 | tee "${1%.sh}.log"
    else
        log_error "file not found: $1"
        exit 1
    fi
else
    log_error "usage: upd [script.sh]"
    log_error "  upd              — run update.sh (or create it via TUI if absent)"
    log_error "  upd my_script.sh — run my_script.sh, log to my_script.log"
    exit 1
fi
"""



    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
        f.write(script)
        tmp = f.name

    try:
        result = subprocess.run(["/bin/bash", tmp] + sys.argv[1:])
    finally:
        os.unlink(tmp)

    sys.exit(result.returncode)
