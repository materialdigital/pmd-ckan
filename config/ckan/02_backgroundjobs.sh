#!/bin/bash
# Auto-create the background jobs API token on first startup.
#
# Checks via the CKAN CLI whether a token named "backgroundjobs" already
# exists for the sysadmin user.  If it does, a previous run already wrote
# the value into ckan.ini — nothing to do.
#
# If no such token exists yet, a new JWT token is minted and written into
# the relevant ckan.ini settings.

_token_list=$(ckan -c "${CKAN_INI}" user token list "${CKAN_SYSADMIN_NAME:-ckan_admin}" 2>/dev/null)
if echo "${_token_list}" | grep -q "backgroundjobs"; then
    echo "[02_backgroundjobs] Token 'backgroundjobs' already exists — skipping token generation."
    return 0
fi

echo "[02_backgroundjobs] No 'backgroundjobs' token found — generating one now..."

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
