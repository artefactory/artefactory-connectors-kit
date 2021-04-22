import streamlit as st
from ack.entrypoints.json.readers import readers_classes
from ack.entrypoints.json.writers import writers_classes
from datetime import datetime, date
import json

from ack.entrypoints.json.main import read_and_write

WRITER_PATH = "../writers"
READER_PATH = "../readers"

reader_dict = {}
writer_dict = {}
result_dict = {"reader": reader_dict, "writers": [writer_dict]}


def datetimeconverter(o):
    if isinstance(o, date):
        return str(o)


def make_recording_widget(f, d):

    def wrapper(json_name, label, *args, **kwargs):
        widget_value = f(label, *args, **kwargs)
        d[json_name] = widget_value
        return widget_value

    return wrapper


def make_recording_list_widget(f, d):

    def wrapper(json_name, label, *args, **kwargs):
        widget_value = f(label, *args, **kwargs)
        d[json_name] = widget_value.strip('][').split(',')
        return widget_value

    return wrapper


def create_field_ui(field, field_name, col, d):

    selectbox = make_recording_widget(col.selectbox, d)
    date_input = make_recording_widget(col.date_input, d)
    checkbox = make_recording_widget(col.checkbox, d)
    number_input = make_recording_widget(col.number_input, d)
    text_input = make_recording_widget(col.text_input, d)
    array_input = make_recording_list_widget(col.text_input, d)
    multi_select = make_recording_widget(col.multiselect, d)

    if "enum" in field:
        selectbox(field_name, field["title"], field["enum"], key=f'{id(d)}{field_name}')
    elif "format" in field and field["format"] == "date-time":
        date_input(field_name, field["title"], datetime.now(), key=f'{id(d)}{field_name}')
    elif field["type"] == 'string':
        default = field.get("default", "")
        text_input(field_name, field["title"], default, key=f'{id(d)}{field_name}')
    elif field["type"] == "array":
        if 'enum' in field['items'] :
            multi_select(field_name, field["title"] + " (array)", field['items']['enum'], key=f'{id(d)}{field_name}')
        else :
            array_input(field_name, field["title"] + " (array)", "[]",
                        help="this must look like ['a','b']", key=f'{id(d)}{field_name}')
    elif field["type"] == "boolean":
        checkbox(field_name, field["title"], [True, False], key=f'{id(d)}{field_name}')
    elif field["type"] == "integer" or field["type"] == "number":
        default = field.get("default", 1)
        number_input(field_name, field["title"], default, key=f'{id(d)}{field_name}')
    else :
        print(NotImplementedError)


def create_ui_schema(schema, col, d, fields):
    exp = col.beta_expander("params")
    for field, field_name, field_opt in zip(schema["properties"].values(), schema["properties"], fields):
        if field_opt.required:
            create_field_ui(field, field_name, exp, d)
        else :
            a = exp.checkbox("use field " + field["title"])
            if a:
                create_field_ui(field, field_name, exp, d)


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
