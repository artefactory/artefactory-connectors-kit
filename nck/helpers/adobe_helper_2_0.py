def build_request_headers(jwt_client):
    """
    Building headers to authenticate with the Reporting API.
    Input: JWTClient object
    """

    return {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(jwt_client.access_token),
        "Content-Type": "application/json",
        "x-api-key": jwt_client.api_key,
        "x-proxy-global-company-id": jwt_client.global_company_id
    }

def add_metrics_container_to_report_description(rep_desc,dimensions,breakdown_item_ids,metrics):
    """
    Filling the metricContainer section of a report description:
    - Creates 1 filter per dimension breakdown x metric
    - Applies filters to each metric
    """

    nb_breakdowns = len(breakdown_item_ids)
    nb_metrics = len(metrics)

    rep_desc["metricContainer"]["metricFilters"] = [
        {
            "id": i+j*nb_breakdowns,
            "type": "breakdown",
            "dimension": f"variables/{dimensions[i]}",
            "itemId": breakdown_item_ids[i]
        }
    for j in range(nb_metrics) for i in range(nb_breakdowns)]

    rep_desc["metricContainer"]["metrics"] = [
        {
            "id": f"metrics/{metrics[j]}",
            "filters": [i+j*nb_breakdowns for i in range(nb_breakdowns)]
        }
    for j in range(nb_metrics)]

    return rep_desc

def get_node_values_from_response(response):
    """
    Extracting dimension values from a report response,
    and returning them into a dictionnary of nodes: {name_itemId: value}
    For instance: {'daterangeday_1200201': 'Mar 1, 2020'}
    """

    name = response["columns"]["dimension"]["id"].split("/")[1]
    values = [row["value"] for row in response["rows"]]
    item_ids = [row["itemId"] for row in response["rows"]]

    return {"{}_{}".format(name,item_id): value for (item_id,value) in zip(item_ids,values)}

def get_item_ids_from_nodes(list_of_strings):
    """
    Extacting item_ids from a list of nodes,
    each node being expressed as 'name_itemId'
    """
    
    return [string.split("_")[1] for string in list_of_strings if string]

def parse_response(response,metrics,parent_dim_parsed):
    """
    Parsing a raw JSON response into the following format:
    {dimension: value, metric: value} (1 dictionnary per row)
    """
        
    dimension = response["columns"]["dimension"]["id"].split("variables/")[1]

    for row in response["rows"]:
        parsed_row_metrics = {m:v for m, v in zip(metrics,row["data"])}
        parsed_row = {**parent_dim_parsed, dimension:row["value"], **parsed_row_metrics}
        yield parsed_row