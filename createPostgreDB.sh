#! /bin/bash
echo "creating db named ... "$USER"_lab6_DB"
cs166_createdb $USER'_lab6_DB'
cs166_db_status
