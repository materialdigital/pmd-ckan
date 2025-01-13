# PMD-CKAN

This composition of applications provides a solution for hosting material science data for projects in the material digital initiative to participate in a decentralized linked data space with a central data portal instance. It also features an ontology agnostic transformation pipeline and a triple store integration.

## Features

- Central Component is a [CKAN](https://ckan.org/) instance as data management system, with default views for pdf, images, text, csv, html, markdown.
- A [apche jena fuseki](https://jena.apache.org/documentation/fuseki2/) triple store at a sublocation /fuseki
- A plugin to create accompanying named graphs in jena fuseki for semantic data contained in ckan datasets including sparql endpoint publication and a user-friendly sparql query interface known as [sparklis](https://github.com/sebferre/sparklis)
- a pipeline for transforming complex csv data common in the domain to [csvw metadata](https://www.w3.org/ns/csvw)
- A rule based mapping pipeline to combine rdf containing data with knowledge graphs to represent material data, its measurement routine and the processing. A tutorial and the steps involved can be found [here](https://github.com/Mat-O-Lab/IOFMaterialsTutorial).

## Prerequisites

Before you begin, make sure you have the following installed:

- Docker
- Docker Compose

## Installation

1. Clone this repository to your local machine and init submoduls:
    ```bash
    git clone https://github.com/materialdigital/pmd-ckan.git
    git submodule update --init
    ```

2. Navigate to the pmd-ckan directory:
    ```bash
    cd ckan-docker-compose
    ```

3. create a .env file, use (example.env)[config/example.env] as a template

    **all variables starting with CKANEXT__ will be translated to the ckan.ini removing CKANINI__, replacing "__" with "."  and putting the name to lowercase**
    examples:
    CKANINI__CSVTOCSVW__FORMATS -> csvtocsvw.formats 
    CKANINI__CSVTOCSVW__SSL_VERIFY -> csvtocsvw.ssl_verify 

4. replace all values in <> braces or are comented to be changed
5. make changes according to your ssl or proxy configuration in [config/nginx/default.template](config/nginx/default.template)
6. Run the docker compose stack, it will pull and build the necessary containers
    ```bash
    docker-compose up
    ```
7. After first successful startup, login into ckan with the admin password you defined in your .env

8. **create an API token for the supervisor background tasks** at /user/<ckan_admin_user>/api-tokens, and paste it into your .env file at BACKGROUNDJOBS_API_TOKEN

9. restart the docker compose stack in detached mode
    ```bash
    docker-compose down
    docker-compose up -d
    ```

7. create a api token for the supervisor background tasks at /user/<ckan_admin_user>/api-tokens, and paste it into your .env file at BACKGROUNDJOBS_API_TOKEN
8. restart the dockercompose stack in detached mode
```bash
docker-compose down
docker-compose up -d
```
---
# Acknowledgments
The authors would like to thank the Federal Government and the Heads of Government of the Länder for their funding and support within the framework of the [Platform Material Digital](https://www.materialdigital.de) consortium. Funded by the German [Federal Ministry of Education and Research (BMBF)](https://www.bmbf.de/bmbf/en/) through the [MaterialDigital](https://www.bmbf.de/SharedDocs/Publikationen/de/bmbf/5/31701_MaterialDigital.pdf?__blob=publicationFile&v=5) Call in Project [KupferDigital](https://www.materialdigital.de/project/1) - project id 13XP5119.
