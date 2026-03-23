#!/bin/bash
# Revoke any existing 'backgroundjobs' token and mint a fresh one on every startup,
# then write it into ckan.ini for all extensions that need it.

echo "[02_backgroundjobs] Revoking old 'backgroundjobs' token (if any)..."
ckan -c "${CKAN_INI}" user token revoke "${CKAN_SYSADMIN_NAME:-ckan_admin}" backgroundjobs 2>/dev/null || true

echo "[02_backgroundjobs] Generating new 'backgroundjobs' token..."
TOKEN=$(ckan -c "$CKAN_INI" user token add "${CKAN_SYSADMIN_NAME:-ckan_admin}" backgroundjobs 2>/dev/null | tail -1 | tr -d '[:space:]')

if [[ -z "$TOKEN" ]]; then
    echo "[02_backgroundjobs] ERROR: Failed to generate API token. Is the DB initialised?" >&2
    return 1
fi

echo ""
echo "================================================================"
echo "  Generated BACKGROUNDJOBS_API_TOKEN"
echo ""
echo "  BACKGROUNDJOBS_API_TOKEN=${TOKEN}"
echo "================================================================"
echo ""

# Write the token into ckan.ini for all extensions that need it.
# All three read from toolkit.config.get("ckanext.<ext>.ckan_token").
ckan config-tool "$CKAN_INI" \
    "ckanext.csvtocsvw.ckan_token=${TOKEN}" \
    "ckanext.csvwmapandtransform.ckan_token=${TOKEN}" \
    "ckanext.fuseki.ckan_token=${TOKEN}"

echo "[02_backgroundjobs] Token written to ckan.ini settings."
