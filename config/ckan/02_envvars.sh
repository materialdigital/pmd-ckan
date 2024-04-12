#!/bin/bash

temp_ini="options.ini"

function configure_ckan_datapusher {
  touch $temp_ini
  for var in $(env | grep "^CKANINI" | cut -d= -f1); do
    variable_name=$(echo "${var#CKANINI__}" | tr '[:upper:]' '[:lower:]' | sed 's/__/\./g')
    value=$(eval "echo \$$var")
    echo "$var -> ${variable_name}=${value}"
    echo "${variable_name}=${value}" >> $temp_ini
  done
  ckan config-tool $CKAN_INI -f $temp_ini
  rm $temp_ini
}

configure_ckan_datapusher