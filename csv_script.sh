#!/bin/sh

FILE=$1

if [ -z "$FILE" ]
then
	echo "Please give a file to convert"
	exit
fi

if [ ! -e "$FILE" ]
then
	echo "$FILE does not exist"
	exit
fi

cp "$FILE" ".$FILE.backup"

sed -i -e "s/\ mW//g" $FILE
sed -i -e "s/\ V//g" $FILE
sed -i -e "s/\ mA//g" $FILE
