# PMD-CKAN

This composition of applications provides a solution for hosting material science data for projects in the material digital initiative to paticipate in a decentralized linked data space with a central data portal instance. It also features ontology agnostic transformation pipelin and a triple store integration.

## Features

- Central Component is a [CKAN](https://ckan.org/) instance as data mangement system, with default views for pdf, images, text, csv, html, markdown.
- A [apche jena fuseki](https://jena.apache.org/documentation/fuseki2/) triple store at a sublocation /fuseki
- A plugin to create accompaniing named graphs in jena fuseki for sematic data contained in ckan datasets including sparql endpint publication and a user friendly sparql query interface known as [sparklis](https://github.com/sebferre/sparklis)
- a pipeline for transforming complex csv data common in the domain to [csvw metadata](https://www.w3.org/ns/csvw)
- A rule based mapping pipeline to combine rdf containing data with knowledge graphs to represent material data,its measurement routine and the processing. A tutorial and the steps involved can be found [here](https://github.com/Mat-O-Lab/IOFMaterialsTutorial).

## Prerequisites

Before you begin, make sure you have the following installed:

- Docker
- Docker Compose

## Installation

1. Clone this repository to your local machine:
```bash
git clone https://github.com/materialdigital/pmd-ckan.git
```

2. Navigate to the pmd-ckan directory:
```bash
cd ckan-docker-compose
```

3. create a .env file, use (example.env)[config/example.env] as template 

**all varaibles starting with CKANEXT__ will be translated to the ckan.ini removing CKANINI__, replacing __ with . and puting the name to lowercase**
examples:
CKANINI__CSVTOCSVW__FORMATS -> csvtocsvw.formats 
CKANINI__CSVTOCSVW__SSL_VERIFY -> csvtocsvw.ssl_verify 

4. Run the docker compose stack, it wil pull and build the neccessary containers
```bash
docker-compose up
```

---
# Acknowledgments
The authors would like to thank the Federal Government and the Heads of Government of the Länder for their funding and support within the framework of the [Platform Material Digital](https://www.materialdigital.de) consortium. Funded by the German [Federal Ministry of Education and Research (BMBF)](https://www.bmbf.de/bmbf/en/) through the [MaterialDigital](https://www.bmbf.de/SharedDocs/Publikationen/de/bmbf/5/31701_MaterialDigital.pdf?__blob=publicationFile&v=5) Call in Project [KupferDigital](https://www.materialdigital.de/project/1) - project id 13XP5119.
