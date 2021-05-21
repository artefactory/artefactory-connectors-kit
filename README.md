# Artefactory Connectors Kit

**ACK is an E(T)L tool specialized in API data ingestion. It is accessible through a Command-Line Interface. The application allows you to easily extract, stream and load data (with minimum transformations), from the API source to the destination of your choice.**

As of now, the most common output format of data loaded by the application is .njson (i.e. a file of n lines, where each line is a json-like dictionary).

Official documentation is available [here](https://artefactory.github.io/artefactory-connectors-kit/).

---

## Philosophy

The application is composed of **3 main components** (*implemented as Python classes*). When combined, these components act as an E(T)L pipeline, allowing you to stream data from a source to the destination of your choice:

- [Readers](ack/readers) are reading data from an API source, and transform it into a stream object.
- [Streams](ack/streams) (*transparent to the end-user*) are local objects used by writers to process individual records collected from the source.
- [Writers](ack/writers) are writing the output stream object to the destination of your choice.

## Why not Airbyte ?

[Airbyte](https://github.com/airbytehq/airbyte) is an open source project that has a mission to make data integration pipelines a commodity.
We love this project and would probably not encourage using ACK to connect data that could be already connected with Airbyte.
You can still use ACK if some of your data has no connector available in Airbyte yet.
The list of connectors unavailable in Airbyte will most certainly reduce over time following the introduction of the [Python Connector Development Kit](https://github.com/airbytehq/airbyte/tree/master/airbyte-cdk/python).

## Available connectors

As of now, the application is offering the following Readers & Writers:
 
### Readers

- **Analytics**
    - Adobe Analytics 1.4
    - Adobe Analytics 2.0
    - Google Analytics (available in Airbyte)
- **Advertising - Adserver**
    - Google Campaign Manager
- **Advertising - DSP**
    - Google Display & Video 360
    - The Trade Desk
- **Advertising - Search**
    - Google Ads (available in Airbyte)
    - Google Search Ads 360
    - Google Search Console
    - Yandex Campaign
    - Yandex Statistics
- **Advertising - Social**
    - Facebook Marketing (available in Airbyte)
    - MyTarget
    - Radarly
    - Twitter Ads
- **CRM**
    - SalesForce (available in Airbyte)
- **Databases**
    - MySQL (available in Airbyte)
- **DevTools**
    - Confluence
- **Files (.csv, .njson)**
    - Amazon S3
    - Google Cloud Storage
    - Google Sheets (available in Airbyte)

### Writers

- **Data Warehouses**
    - Google BigQuery (available in Airbyte)
- **Debugging**
    - Console
- **Files (.njson)**
    - Amazon S3
    - Google Cloud Storage
    - Local file (available in Airbyte)
