#!/bin/sh

if nginx -t && nginx -s reload; then
    exit 0
else
    exit 1
fi
