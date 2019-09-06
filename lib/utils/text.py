
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
        


def get_generator_dict_from_str_csv(line_iterator):
    got_header = False
    headers = []
    for line in line_iterator:
        if line == '':
            break
        if not got_header:
            headers = line.decode("utf-8").split(',')
            got_header = True
        else :
            values = line.decode("utf-8").split(',')
            yield {headers[i]:values[i] for i in range(len(headers))}