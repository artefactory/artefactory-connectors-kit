import streamlit as st
from ack.entrypoints.json.readers import readers_classes
from ack.entrypoints.json.writers import writers_classes
from ack.ui.helpers import create_ui_schema, datetimeconverter
import json

from ack.entrypoints.json.main import read_and_write

st.set_page_config(layout="wide")

WRITER_PATH = "../writers"
READER_PATH = "../readers"

reader_dict = {}
writer_dict = {}
result_dict = {"reader": reader_dict, "writers": [writer_dict]}

st.header("ACK UI : The best way to test out ACK")

reader_col, writer_col = st.beta_columns(2)

reader = reader_col.selectbox("choose a reader", options=list(readers_classes.keys()))
reader_fields = readers_classes[reader][1].__fields__.values()
writer = writer_col.selectbox("choose a writer", options=list(writers_classes.keys()))
writer_fields = readers_classes[reader][1].__fields__.values()
reader_schema = readers_classes[reader][1].schema()
if len(writers_classes[writer]) > 1:
    writer_schema = writers_classes[writer][1].schema()
    create_ui_schema(writer_schema, writer_col, writer_dict, writer_fields)


create_ui_schema(reader_schema, reader_col, reader_dict, reader_fields)

st.text("")
jsonbutton = st.button("generate JSON")
lauchbutton = st.button("launch")

reader_dict["name"] = reader
writer_dict["name"] = writer

if jsonbutton :
    st.text(json.dumps(result_dict, default=datetimeconverter, indent=2))

if lauchbutton :
    json_result = json.dumps(result_dict, default=datetimeconverter, indent=2)
    dict_final = json.loads(json_result)
    read_and_write(dict_final)
