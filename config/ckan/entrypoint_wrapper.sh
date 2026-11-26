#!/bin/bash
set -e

echo "CKAN Entrypoint Wrapper: Preparing dev permissions..."

# Only fix permissions if in DEBUG/development mode
if [[ "$DEBUG" == "true" ]]; then
    echo "Debug mode enabled - fixing permissions on mounted volumes..."
    
    # Fix permissions on storage directory
    if [ -d "/var/lib/ckan" ]; then
        chown -R :502 /var/lib/ckan 2>/dev/null || echo "Could not fix permissions on /var/lib/ckan"
        chmod -R 755 /var/lib/ckan 2>/dev/null || echo "Could not fix permissions on /var/lib/ckan"
        echo "Fixed permissions on /var/lib/ckan"
    fi
    
    # Map the container's ckan user onto the host owner of the bind-mounted
    # extensions, so files are editable on the host AND writable in the
    # container, and files created in the container stay owned by the host user.
    # (No chown/chmod on the mount itself - that would change host ownership.)
    if [ -d "$SRC_EXTENSIONS_DIR" ]; then
        HOST_UID=$(stat -c %u "$SRC_EXTENSIONS_DIR")
        OLD_UID=$(id -u ckan)
        if [ "$HOST_UID" != "0" ] && [ "$HOST_UID" != "$OLD_UID" ]; then
            usermod -o -u "$HOST_UID" ckan
            # re-own what the image/volumes had given to the old uid (not the bind mount)
            find /srv/app /var/lib/ckan -xdev -uid "$OLD_UID" -exec chown -h "$HOST_UID" {} + 2>/dev/null || true
            echo "Remapped ckan uid $OLD_UID -> $HOST_UID (owner of $SRC_EXTENSIONS_DIR)"
        fi
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
