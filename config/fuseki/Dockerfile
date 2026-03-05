FROM secoresearch/fuseki:4.9.0

# Copy our custom entrypoint that handles volume mount initialization
# Need to switch to root temporarily to set permissions
USER root

# Copy custom index.html with corrected paths for subpath deployment
COPY index.html /jena-fuseki/webapp/index.html

# set auth on all
RUN sed -i '/^\/\*\*\s*=\s*anon/d' /jena-fuseki/shiro.ini && \
    echo '' >> /jena-fuseki/shiro.ini && \
    echo '## CKAN Security: Require authentication for ALL dataset access' >> /jena-fuseki/shiro.ini && \
    echo '/** = authc, roles[admin]' >> /jena-fuseki/shiro.ini
# Switch back to the fuseki user (UID 1000)
USER 1000

