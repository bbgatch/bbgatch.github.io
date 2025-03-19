#!/bin/zsh
python3 call-jury-services.py
source .env
sqlite3 "$DB_PATH" <<EOF
.mode box
.read review-tables.sql
EOF