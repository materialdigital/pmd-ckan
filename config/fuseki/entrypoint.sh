#!/bin/sh
set -e

# Substitute only ${ADMIN_PASSWORD} so Shiro's $plainMatcher references are untouched
cp /fuseki-init/shiro.ini.tpl /fuseki-base/shiro.ini

exec /docker-entrypoint.sh "$@"
