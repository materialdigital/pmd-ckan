#!/bin/bash

function configure_ckan_datapusher {
  for var in $(env | grep "^CKANINI" | cut -d= -f1); do
    variable_name=$(echo "${var#CKANINI__}" | tr '[:upper:]' '[:lower:]' | sed 's/__/\./g')
    value=$(eval "echo \$$var")
    ckan config-tool $CKAN_INI "${variable_name}=${value}"
    echo "Set ${variable_name} in ${CKAN_INI}"
  done
}

configure_ckan_datapusher