########
Overview
########

**NCK is a Command-Line Interface (CLI), allowing you to easily request, stream and store raw reports, from the API source to the destination of your choice.** As of now, the most common output format of data extracted by the application is .njson (i.e. a file of n lines, where each line is a json-like dictionary).

==========
Philosophy
==========

The application is composed of **3 main components** (*implemented as Python classes*). When combined, these components act as data connectors, allowing you to stream data from a source to the destination of your choice:

- :ref:`readers:Readers` are reading data from an API source, and transform it into a stream object.
- :ref:`streams:Streams` (*transparent to the end-user*) are local objects used by writers to process individual records collected from the source.
- :ref:`writers:Writers` are writing the output stream object to the destination of your choice.

====================
Available connectors
====================

As of now, the application is offering:
 
**21 Readers, in various areas such as Media Activation, Website Analytics & many more**

- Adobe Analytics 1.4
- Adobe Analytics 2.0
- Amazon S3
- Confluence
- Facebook Marketing
- Google Ads
- Google Analytics
- Google Cloud Storage
- Google Campaign Manager
- Google Display & Video 360
- Google Search Ads 360
- Google Search Console
- Google Sheets
- MySQL
- MyTarget
- Radarly
- SalesForce
- The Trade Desk
- Twitter Ads
- Yandex Campaign
- Yandex Statistics

**5 Writers, including destinations to GCP & AWS cloud platforms**

- Amazon S3
- Google BigQuery
- Google Cloud Storage
- Local file
- Console (used for debugging)

*A data connector could be, for instance, the combination of a Google Analytics reader + a Google Cloud Storage writer, collecting data from the Google Analytics API, and storing output stream records into a Google Cloud Storage bucket.*
