# Solr for CKAN 2.12. This is what the ckan/ckan-solr image does (a thin layer on the official Solr), built here so the
# Solr version can follow upstream releases independently of that image.
#
# Update: bump SOLR_VERSION (any 9.x keeps the index format; `ckan search-index rebuild` recreates it if ever needed).
# The schema comes from the CKAN release that the stack runs (config/ckan/Dockerfile: ckan/ckan-base:2.12.1).
ARG SOLR_VERSION=9.11.0
FROM solr:${SOLR_VERSION}

ARG CKAN_REF=ckan-2.12.1
ENV SOLR_CONFIG_DIR=/opt/solr/server/solr/configsets
ENV SOLR_SCHEMA_FILE=${SOLR_CONFIG_DIR}/ckan/conf/managed-schema

USER root
RUN cp -R ${SOLR_CONFIG_DIR}/_default ${SOLR_CONFIG_DIR}/ckan
# CKAN uses none of Solr's optional modules (its solrconfig.xml has no <lib>/module references), so drop them to keep
# the image small.
RUN rm -rf /opt/solr-*/modules /opt/solr-*/contrib /opt/solr/modules /opt/solr/contrib
ADD --chmod=644 https://raw.githubusercontent.com/ckan/ckan/${CKAN_REF}/ckan/config/solr/schema.xml ${SOLR_SCHEMA_FILE}
USER 8983

# creates the core "ckan" on first start, then runs Solr in the foreground
CMD ["sh", "-c", "solr-precreate ckan $SOLR_CONFIG_DIR/ckan"]
