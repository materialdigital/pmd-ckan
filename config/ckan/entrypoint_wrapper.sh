#!/bin/bash
set -e

echo "CKAN Entrypoint Wrapper: Fixing permissions for user 503:502..."

# Only fix permissions if in DEBUG/development mode
if [[ "$DEBUG" == "true" ]]; then
    echo "Debug mode enabled - fixing permissions on mounted volumes..."
    
    # Fix permissions on storage directory
    if [ -d "/var/lib/ckan" ]; then
        chown -R :502 /var/lib/ckan 2>/dev/null || echo "Could not fix permissions on /var/lib/ckan"
        chmod -R 755 /var/lib/ckan 2>/dev/null || echo "Could not fix permissions on /var/lib/ckan"
        echo "Fixed permissions on /var/lib/ckan"
    fi
    
    # Fix permissions on extensions directory (critical for dev mode)
    # Use 775 (rwxrwxr-x) to ensure group has write permissions for editing files
    if [ -d "$SRC_EXTENSIONS_DIR" ]; then
        chown -R :502 "$SRC_EXTENSIONS_DIR" 2>/dev/null || echo "Could not fix permissions on $SRC_EXTENSIONS_DIR"
        chmod -R 775 "$SRC_EXTENSIONS_DIR" 2>/dev/null || echo "Could not fix permissions on $SRC_EXTENSIONS_DIR"
        echo "Fixed permissions on $SRC_EXTENSIONS_DIR (set to 775 for group write access)"
    fi
    
    # Fix permissions on CKAN source directory (needed for dev mode with bind mounts)
    if [ -d "$SRC_DIR" ]; then
        chown -R :502 "$SRC_DIR" 2>/dev/null || echo "Could not fix permissions on $SRC_DIR"
        chmod -R 755 "$SRC_DIR" 2>/dev/null || echo "Could not fix permissions on $SRC_DIR"
        echo "Fixed permissions on $SRC_DIR"
    fi
    
    echo "Permission fixes completed for debug mode."
else
    echo "Production mode - skipping permission fixes."
fi

# Drop to CKAN user and execute the original start script
echo "Switching to user ckan (503:502) and starting CKAN..."

# Check if gosu or su-exec is available for stepping down from root
if command -v gosu &> /dev/null; then
    exec gosu ckan:ckan-sys /srv/app/start_ckan.sh "$@"
elif command -v su-exec &> /dev/null; then
    exec su-exec ckan:ckan-sys /srv/app/start_ckan.sh "$@"
else
    # Fall back to runuser - use user/group names, not numeric IDs
    exec runuser -u ckan -g ckan-sys -- /srv/app/start_ckan.sh "$@"
fi
