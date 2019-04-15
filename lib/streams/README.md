# NCK Streams

Streams are an object that can be read by writers. Readers populate [StreamCollection](./stream.py) which is a list of Streams.

Each stream must implement two methods:

1. Readline: yield each element of a stream, one by one. For example, FileStream yield each line.
2. as_file: transform stream in an IO object. 

Streams need a name and a content object to be created.

## Streams list

1. [File](#File-Stream)
2. [Temporary File](#Temporary-File-Stream)
3. [JSON](#JSON-Stream)

## File Stream

Content of the stream is an IO object.

as_file: Returns FileIO object
readline: Returns each line of the file

## Temporary File Stream

Extension of a [File Stream](#File-Stream). 

as_file: Returns TempFile IO Object
readline: Returns each line of the file

## JSON Stream

Extension of [Temporary File Stream](#Temporary-File-Stream)

as_file: Returns TempFile IO Object
readline: Returns a normalized Dict where keys are columns and values content of the column.