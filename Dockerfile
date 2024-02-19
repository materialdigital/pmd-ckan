FROM ckan/ckan-dev:2.10.3
#FROM ckan/ckan-base:2.9.9-dev


ENV APP_DIR=/srv/app
ENV TZ=UTC
RUN echo ${TZ} > /etc/timezone


# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
        cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;

# Install any extensions needed by your CKAN instance
# - Make sure to add the plugins to CKAN__PLUGINS in the .env file
# - Also make sure all provide all extra configuration options, either by:
#   * Adding them to the .env file (check the ckanext-envvars syntax for env vars), or
#   * Adding extra configuration scripts to /docker-entrypoint.d folder) to update
#      the CKAN config file (ckan.ini) with the `ckan config-tool` command
#
# See README > Extending the base images for more details

# For instance:
#
### XLoader ###
#RUN pip3 install -e 'git+https://github.com/ckan/ckanext-xloader.git@master#egg=ckanext-xloader' && \ 
#    pip3 install -r ${APP_DIR}/src/ckanext-xloader/requirements.txt && \
#    pip3 install -U requests[security]

# ## Harvester ###
# RUN pip3 install -e 'git+https://github.com/ckan/ckanext-harvest.git@master#egg=ckanext-harvest' && \
#    pip3 install -r ${APP_DIR}/src/ckanext-harvest/pip-requirements.txt
# will also require gather_consumer and fetch_consumer processes running (please see https://github.com/ckan/ckanext-harvest)

### Scheming ###
#RUN  pip3 install -e 'git+https://github.com/ckan/ckanext-scheming.git@master#egg=ckanext-scheming'

### Pages ###
#RUN  pip3 install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages

# ## DCAT ###
# RUN  pip3 install -e git+https://github.com/ckan/ckanext-dcat.git@v0.0.6#egg=ckanext-dcat && \
#     pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-dcat/v0.0.6/requirements.txt

### CSVTOCSVW
RUN  pip3 install -e git+https://github.com/Mat-O-Lab/ckanext-csvtocsvw.git#egg=ckanext-csvtocsvw && \
     pip3 install -r https://raw.githubusercontent.com/Mat-O-Lab/ckanext-csvtocsvw/master/requirements.txt

### CSVWMAPANDTRANSFORM
RUN  pip3 install -e git+https://github.com/Mat-O-Lab/ckanext-csvwmapandtransform.git#egg=ckanext-csvwmapandtransform && \
     pip3 install -r https://raw.githubusercontent.com/Mat-O-Lab/ckanext-csvwmapandtransform/master/requirements.txt

### HARVEST
RUN pip3 install -e git+https://github.com/ckan/ckanext-harvest.git#egg=ckanext-harvest && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-harvest/master/requirements.txt

### DCAT
RUN pip3 install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat  && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-dcat/master/requirements.txt

### DCATDE-AP
RUN pip3 install -e git+https://github.com/GovDataOfficial/ckanext-dcatde.git#egg=ckanext-dcatde && \
    pip3 install -r https://raw.githubusercontent.com/GovDataOfficial/ckanext-dcatde/master/base-requirements.txt

### FUSEKI
RUN pip3 install -e git+https://github.com/Mat-O-Lab/ckanext-fuseki.git#egg=ckanext-fuseki && \
    pip3 install -r https://github.com/Mat-O-Lab/ckanext-fuseki/raw/master/requirements.txt

### PDFView
RUN pip3 install ckanext-pdfview


# Clone the extension(s) your are writing for your own project in the `src` folder
# to get them mounted in this image at runtime

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
# Copy custom initialization scripts
COPY docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY patches ${APP_DIR}/patches

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
