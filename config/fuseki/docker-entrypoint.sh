#!/bin/bash
set -e

# Custom entrypoint wrapper for secoresearch/fuseki:4.9.0
# Adds CKAN security: Disables anonymous access to datasets

echo "Starting Fuseki with CKAN security (disabling anonymous dataset access)..."

# Function to add authentication requirement to shiro.ini
add_auth_requirement() {
    local shiro_file="$1"
    
    if [ -f "$shiro_file" ]; then
        # Check if our security rule already exists
        if ! grep -q "^/\*\* = authc, roles\[admin\]" "$shiro_file"; then
            echo "Adding authentication requirement to $shiro_file..."
            
            # Remove any existing /** = anon line
            sed -i '/^\/\*\* = anon/d' "$shiro_file"
            
            # Add our security rule at the end
            echo "" >> "$shiro_file"
            echo "## CKAN Security: Require authentication for ALL dataset access" >> "$shiro_file"
            echo "/** = authc, roles[admin]" >> "$shiro_file"
            
            echo "Security modification applied to $shiro_file"
        else
            echo "Security rule already exists in $shiro_file"
        fi
    else
        echo "Warning: $shiro_file not found, will be created by base entrypoint"
    fi
}

# Modify shiro.ini in FUSEKI_HOME (template used by base entrypoint)
FUSEKI_HOME="/jena-fuseki"
add_auth_requirement "$FUSEKI_HOME/shiro.ini"

# The base entrypoint will copy shiro.ini to FUSEKI_BASE and set password
# We'll modify it again after the base entrypoint runs, but do it in background
# to avoid blocking startup

# Start background task to modify FUSEKI_BASE/shiro.ini after creation
(
    sleep 2  # Give base entrypoint time to create the file
    FUSEKI_BASE="${FUSEKI_BASE:-/fuseki-base}"
    add_auth_requirement "$FUSEKI_BASE/shiro.ini"
) &

# Execute the original Fuseki entrypoint with the base image's CMD
# The base image CMD is: java -cp "*:/javalibs/*" org.apache.jena.fuseki.cmd.FusekiCmd
exec /docker-entrypoint.sh java -cp "*:/javalibs/*" org.apache.jena.fuseki.cmd.FusekiCmd "$@"
