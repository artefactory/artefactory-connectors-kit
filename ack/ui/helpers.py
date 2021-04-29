from datetime import datetime, date


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


def create_field_ui(field, field_name, col, d, title):

    selectbox = make_recording_widget(col.selectbox, d)
    date_input = make_recording_widget(col.date_input, d)
    checkbox = make_recording_widget(col.checkbox, d)
    number_input = make_recording_widget(col.number_input, d)
    text_input = make_recording_widget(col.text_input, d)
    array_input = make_recording_list_widget(col.text_input, d)
    multi_select = make_recording_widget(col.multiselect, d)

    if "enum" in field:
        selectbox(field_name, field["title"], field["enum"], key=f'{title}{field_name}')
    elif "format" in field and field["format"] == "date-time":
        date_input(field_name, field["title"], datetime.now(), key=f'{title}{field_name}')
    elif field["type"] == 'string':
        default = field.get("default", "")
        text_input(field_name, field["title"], default, key=f'{title}{field_name}')
    elif field["type"] == "array":
        if 'enum' in field['items'] :
            multi_select(field_name, field["title"] + " (array)", field['items']['enum'], key=f'{title}{field_name}')
        else :
            array_input(field_name, field["title"] + " (array)", "[]",
                        help="this must look like ['a','b']", key=f'{title}{field_name}')
    elif field["type"] == "boolean":
        checkbox(field_name, field["title"], [True, False], key=f'{title}{field_name}')
    elif field["type"] == "integer" or field["type"] == "number":
        default = field.get("default", 1)
        number_input(field_name, field["title"], default, key=f'{title}{field_name}')
    else :
        raise NotImplementedError


def create_ui_schema(schema, col, d, fields):
    exp = col.beta_expander("params")
    for field, field_name, field_opt in zip(schema["properties"].values(), schema["properties"], fields):
        if field_opt.required:
            create_field_ui(field, field_name, exp, d, schema["title"])
        else :
            a = exp.checkbox("use field " + field["title"])
            if a:
                create_field_ui(field, field_name, exp, d, schema["title"])
