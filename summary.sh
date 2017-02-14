#!/bin/bash
#
# 统计最近几天的请求情况(假设没6min请求一次，一天240次)
# $1 - 最近几天
#

days=$1
BILIVE_LOG='./bilive.log'

echo_red()
{
	echo -e "$1:\033[31m $2 \033[0m"
}

for i in $(seq $days); do 
	date=$(date +'%Y-%m-%d' -d "$i days ago")
	cnt=$(cat $BILIVE_LOG | grep $date | wc -l)

	if [ "$cnt" == "240" ]; then
		echo "$date: $cnt" 
	else
		echo_red $date $cnt	
	fi
done


