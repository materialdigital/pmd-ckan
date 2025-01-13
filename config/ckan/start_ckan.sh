#!/bin/bash

if [[ -z "${DEBUG}" ]]; then
  DEBUG=false
fi

# Install any local extensions in the src_extensions volume
if $DEBUG; then
    echo "Looking for local extensions to install..."
    echo "Extension dir contents:"
    ls -la $SRC_EXTENSIONS_DIR
    for i in $SRC_EXTENSIONS_DIR/*
    do
        if [ -d $i ];
        then
            if [ -d $SRC_DIR/$(basename $i) ];
            then
                pip uninstall -y "$(basename $i)"
            fi

            if [ -f $i/pip-requirements.txt ];
            then
                pip3 install -r $i/pip-requirements.txt
                echo "Found requirements file in $i"
            fi
            if [ -f $i/requirements.txt ];
            then
                pip3 install -r $i/requirements.txt
                echo "Found requirements file in $i"
            fi
            if [ -f $i/dev-requirements.txt ];
            then
                pip3 install -r $i/dev-requirements.txt
                echo "Found dev-requirements file in $i"
            fi
            if [ -f $i/setup.py ];
            then
                cd $i
                python3 $i/setup.py develop
                echo "Found setup.py file in $i"
                cd $APP_DIR
            fi
            if [ -f $i/pyproject.toml ];
            then
                cd $i
                pip3 install -e .
                echo "Found pyproject.toml file in $i"
                cd $APP_DIR
            fi

            # Point `use` in test.ini to location of `test-core.ini`
            if [ -f $i/test.ini ];
            then
                echo "Updating \`test.ini\` reference to \`test-core.ini\` for plugin $i"
                ckan config-tool $i/test.ini "use = config:../../src/ckan/test-core.ini"
            fi
        fi
    done
    # Set debug to true
    echo "Enabling debug mode"
    ckan config-tool $CKAN_INI -s DEFAULT "debug = true"

    # Update test-core.ini DB, SOLR & Redis settings
    echo "Loading test settings into test-core.ini"
    ckan config-tool $SRC_DIR/ckan/test-core.ini \
        "sqlalchemy.url = $TEST_CKAN_SQLALCHEMY_URL" \
        "ckan.datastore.write_url = $TEST_CKAN_DATASTORE_WRITE_URL" \
        "ckan.datastore.read_url = $TEST_CKAN_DATASTORE_READ_URL" \
        "solr_url = $TEST_CKAN_SOLR_URL" \
        "ckan.redis.url = $TEST_CKAN_REDIS_URL"
    CKAN_RUN="ckan -c $CKAN_INI run -H 0.0.0.0"
    CKAN_OPTIONS=""
    if [ "$USE_DEBUGPY_FOR_DEV" = true ] ; then
        pip install debugpy
        CKAN_RUN="/usr/bin/python -m debugpy --listen 0.0.0.0:5678 $CKAN_RUN"
        CKAN_OPTIONS="$CKAN_OPTIONS --disable-reloader"
    fi

    if [ "$USE_HTTPS_FOR_DEV" = true ] ; then
        CKAN_OPTIONS="$CKAN_OPTIONS -C unsafe.cert -K unsafe.key"
    fi
fi


# Set up the secrets Flask
if grep -qE "SECRET_KEY ?= ?$" ckan.ini
then
    if [[ -z "${SECRET_KEY}" ]]; then
        echo "Generating new SECRET_KEY"
        SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')
    else
        echo "Using existing SECRET_KEY from environment"
    fi

    echo "Setting SECRET_KEY in ini file"
    ckan config-tool $CKAN_INI "SECRET_KEY=${SECRET_KEY}"
fi

if grep -qE "api_token.jwt.encode.secret ?= ?$" ckan.ini
then
    if [[ -z "${JWT_SECRET}" ]]; then
    echo "Generating new JWT_SECRET"
    JWT_SECRET=$(python3 -c 'import secrets; print("string:" + secrets.token_urlsafe())')
    fi
    echo "Setting JWT_SECRETs in ini file"
    ckan config-tool $CKAN_INI "api_token.jwt.encode.secret=${JWT_SECRET}"
    ckan config-tool $CKAN_INI "api_token.jwt.decode.secret=${JWT_SECRET}"
fi

if grep -qE "WTF_CSRF_SECRET_KEY ?= ?$" ckan.ini
then
    if [[ -z "${WTF_CSRF_SECRET_KEY}" ]]; then
    echo "Generating new WTF_CSRF_SECRET_KEY"
    WTF_CSRF_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')
    fi
    echo "Setting WTF_CSRF_SECRET in ini file"
    ckan config-tool $CKAN_INI "WTF_CSRF_SECRET_KEY=${WTF_CSRF_SECRET_KEY}"
fi



# Run the prerun script to init CKAN and create the default admin user
python3 prerun.py

# Run any startup scripts provided by images extending this one
if [[ -d "/docker-entrypoint.d" ]]
then
    for f in /docker-entrypoint.d/*; do 
        case "$f" in
            *.sh)     echo "$0: Running init file $f"; . "$f" ;;
            *.py)     echo "$0: Running init file $f"; python3 "$f"; echo ;;
            *)        echo "$0: Ignoring $f (not an sh or py file)" ;;
        esac
    done
fi

# --plugins-dir /usr/lib/uwsgi/plugins \
#             --plugins http,python \

# Set the common uwsgi options
UWSGI_OPTS="--socket /tmp/uwsgi.sock \
            --wsgi-file /srv/app/wsgi.py \
            --module wsgi:application \
            --http 0.0.0.0:5000 \
            --master --enable-threads \
            --lazy-apps \
            -p 2 -L -b 32768 --vacuum \
            --harakiri $UWSGI_HARAKIRI"

if $DEBUG; then
    # Start the development server as the ckan user with automatic reload
    echo Starting development server.
    while true; do
        $CKAN_RUN $CKAN_OPTIONS
        echo Exit with status $?. Restarting.
        sleep 2
    done
else
    # Start uwsgi
    uwsgi $UWSGI_OPTS
fi


