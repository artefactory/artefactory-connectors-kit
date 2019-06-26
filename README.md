# nautilus-connectors-kit

Nautilus connectors kit is a tool which aim is getting raw data from different sources and store them as-is into different destinations (GCS, BQ, local files, etc.).

## Philosophy

NCK is divided in three main components : Readers, Streams, and Writers.

- [Readers](./lib/readers/README.md) role is to read data from distant sources and transform it into stream object
- [Streams](./lib/streams/README.md) role is to be read as file or line by line. There are local objects usable by writers
- [Writers](./lib/writers/README.md) role is to write stream into distant location

## Usage

### Docker image

1. Build Docker image using `make build_base_image`
2. Run image to get help `docker run --rm nautilus-connector-kit:latest --help`
