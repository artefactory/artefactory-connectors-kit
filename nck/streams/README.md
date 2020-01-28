# NCK Streams

Streams are an object that can be read by writers.
Each stream must implement the following methods:

1. `readlines`: yield each element of a stream, one by one.

Streams need a name and a content object to be created.
