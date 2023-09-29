# DataStack
Docker Compose Stack to transform Material Science Data into Sematic Data

# create a .env file with, but set at list values with <> 
```bash
# Container names
NGINX_CONTAINER_NAME=nginx
REDIS_CONTAINER_NAME=redis
POSTGRESQL_CONTAINER_NAME=db_ckan
SOLR_CONTAINER_NAME=solr
DATAPUSHER_CONTAINER_NAME=datapusher
CKAN_CONTAINER_NAME=ckan
WORKER_CONTAINER_NAME=ckan-worker

# Host Ports
CKAN_PORT_HOST=5000
NGINX_PORT_HOST=80
NGINX_SSLPORT_HOST=443

# CKAN databases
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_HOST=db
CKAN_DB_USER=ckandbuser
CKAN_DB_PASSWORD=ckandbpassword
CKAN_DB=ckandb
DATASTORE_READONLY_USER=datastore_ro
DATASTORE_READONLY_PASSWORD=datastore
DATASTORE_DB=datastore
CKAN_SQLALCHEMY_URL=postgresql://ckandbuser:ckandbpassword@db/ckandb
CKAN_DATASTORE_WRITE_URL=postgresql://ckandbuser:ckandbpassword@db/datastore
CKAN_DATASTORE_READ_URL=postgresql://datastore_ro:datastore@db/datastore

# Test database connections
TEST_CKAN_SQLALCHEMY_URL=postgres://ckan:ckan@db/ckan_test
TEST_CKAN_DATASTORE_WRITE_URL=postgresql://ckan:ckan@db/datastore_test
TEST_CKAN_DATASTORE_READ_URL=postgresql://datastore_ro:datastore@db/datastore_test

# CKAN core
CKAN_PORT=5000
CKAN_VERSION=2.10.0
CKAN_SITE_ID=default
CKAN_SITE_URL=http://ckan:${CKAN_PORT}
CKAN___BEAKER__SESSION__SECRET=<session_secret>

# See https://docs.ckan.org/en/latest/maintaining/configuration.html#api-token-settings
CKAN___API_TOKEN__JWT__ENCODE__SECRET=string:<encode_secret>
CKAN___API_TOKEN__JWT__DECODE__SECRET=string:<decode_secret>
CKAN_SYSADMIN_NAME=ckan_admin
CKAN_SYSADMIN_PASSWORD=<admin_pass>
CKAN_SYSADMIN_EMAIL=admin@example.com
CKAN_STORAGE_PATH=/var/lib/ckan
# CKAN_SMTP_SERVER=smtp.corporateict.domain:25
# CKAN_SMTP_STARTTLS=True
# CKAN_SMTP_USER=user
# CKAN_SMTP_PASSWORD=pass
# CKAN_SMTP_MAIL_FROM=ckan@localhost
TZ=UTC

# Solr
SOLR_IMAGE_VERSION=2.9-solr8
CKAN_SOLR_URL=http://solr:8983/solr/ckan
TEST_CKAN_SOLR_URL=http://solr:8983/solr/ckan

# Redis
REDIS_VERSION=6
CKAN_REDIS_URL=redis://redis:6379/1
TEST_CKAN_REDIS_URL=redis://redis:6379/1

# Datapusher
DATAPUSHER_VERSION=0.0.20
CKAN_DATAPUSHER_URL=http://datapusher:8800
CKAN__DATAPUSHER__CALLBACK_URL_BASE=http://ckan:${CKAN_PORT}
DATAPUSHER_REWRITE_RESOURCES=True
DATAPUSHER_REWRITE_URL=http://ckan:${CKAN_PORT}

# NGINX
NGINX_PORT=80
NGINX_SSLPORT=443
CKAN_PROXY_PASS=http://ckan:${CKAN_PORT}

# Extensions
SRC_EXTENSIONS_DIR=/srv/app/src_extensions
CKAN__PLUGINS="envvars image_view text_view recline_view datastore datapusher csvtocsvw"
CKAN__HARVEST__MQ__TYPE=redis
CKAN__HARVEST__MQ__HOSTNAME=redis
CKAN__HARVEST__MQ__PORT=6379
CKAN__HARVEST__MQ__REDIS_DB=1
```

# Run flask app
```bash
docker-compose up
```

```bash
