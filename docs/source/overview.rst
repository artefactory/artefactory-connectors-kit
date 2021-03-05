########
Overview
########

**NCK is an ET(L) tool specialized in API data ingestion. It is accessible through a Command-Line Interface. The application allows you to easily extract, stream and load data (with minimum transformations), from the API source to the destination of your choice.**

As of now, the most common output format of data loaded by the application is .njson (i.e. a file of n lines, where each line is a json-like dictionary).

==========
Philosophy
==========

The application is composed of **3 main components** (*implemented as Python classes*). When combined, these components act as an EL(T) pipeline, allowing you to stream data from a source to the destination of your choice:

- :ref:`readers:Readers` are reading data from an API source, and transform it into a stream object.
- :ref:`streams:Streams` (*transparent to the end-user*) are local objects used by writers to process individual records collected from the source.
- :ref:`writers:Writers` are writing the output stream object to the destination of your choice.

====================
Available connectors
====================

As of now, the application is offering the following Readers & Writers:

*******
Readers
*******  

- **Analytics**
    - Adobe Analytics 1.4
    - Adobe Analytics 2.0
    - Google Analytics
- **Advertising - Adserver**
    - Google Campaign Manager
- **Advertising - DSP**
    - Google Display & Video 360
    - The Trade Desk
- **Advertising - Search**
    - Google Ads
    - Google Search Ads 360
    - Google Search Console
    - Yandex Campaign
    - Yandex Statistics
- **Advertising - Social**
    - Facebook Marketing
    - MyTarget
    - Radarly
    - Twitter Ads
- **CRM**
    - SalesForce
- **Databases**
    - MySQL
- **DevTools**
    - Confluence
- **Files (.csv, .njson)**
    - Amazon S3
    - Google Cloud Storage
    - Google Sheets

*******
Writers
*******

- **Data Warehouses**
    - Google BigQuery
- **Debugging**
    - Console
- **Files (.njson)**
    - Amazon S3
    - Google Cloud Storage
    - Local file
