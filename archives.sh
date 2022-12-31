#!/bin/bash

Last_Month=$(date --date="last month" +%Y-%m)
My_Path=$(dirname "$0")
Log_Path="$My_Path/log"
Arc_Path="$Log_Path/archives"
[[ ! -d "$Arc_Path" ]] && mkdir "$Arc_Path"
Files=$(ls "$Log_Path")
Archive="$Arc_Path/$Last_Month.tar.gz"
Files_To_Archive=$(echo "$Files" | grep "$Last_Month\-")
# echo "$Files_To_Archive"
cd "$Log_Path" || exit
tar -zcf "$Archive" $Files_To_Archive
rm $Files_To_Archive
