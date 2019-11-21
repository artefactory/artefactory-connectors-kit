from typing import Union, Generator, Dict


def add_column_value_to_csv_line_iterator(line_iterator, columname, value):
    first_line = True
    for line in line_iterator:
        if line == '':
            break
        if first_line:
            first_line = False
            if columname in line.split(','):
                raise Exception('Column {} already present'.format(columname))
            yield line + ',' + columname
        else:
            yield line + ',' + value


def get_generator_dict_from_str_csv(
    line_iterator: Generator[Union[bytes, str], None, None]
) -> Generator[Dict[str, str], None, None]:
    headers = next(line_iterator).decode("utf-8").split(",")
    for line in line_iterator:
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="ignore")
        if line == '':
            break
        else:
            yield dict(zip(headers, line.split(',')))
