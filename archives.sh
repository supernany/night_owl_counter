#!/bin/bash
# encoding: utf-8

LAST_MONTH=$(date --date="last month" +%Y-%m)
MY_PATH=$(dirname "$0")
LOG_PATH="$MY_PATH/log"
ARC_PATH="$LOG_PATH/archives"
[[ ! -d "$ARC_PATH" ]] && mkdir "$ARC_PATH"
FILES=$(ls "$LOG_PATH")
ARCHIVE="$ARC_PATH/$LAST_MONTH.tar.gz"
FILES_TO_ARCHIVE=$(echo "$FILES" | grep "$LAST_MONTH\-")
cd "$LOG_PATH" || exit
tar -zcf "$ARCHIVE" "$FILES_TO_ARCHIVE"
rm "$FILES_TO_ARCHIVE"
