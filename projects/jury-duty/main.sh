#!/bin/zsh
python3 call-jury-services.py
sqlite3 jury_duty.db <<EOF
.mode box
.read review-tables.sql
EOF