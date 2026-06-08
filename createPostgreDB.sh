#! /bin/bash
echo "creating db named ... "$USER"_DB"
cs166_createdb $USER'_DB'
cs166_db_status
