POSSIBLE_REQUEST_TYPES = [
    "existing_query",
    "custom_query",
    "existing_query_report",
    "custom_query_report",
    "lineitems_objects",
    "sdf_objects",
    "list_reports",
]

POSSIBLE_SDF_FILE_TYPES = [
    "INVENTORY_SOURCE",
    "AD",
    "AD_GROUP",
    "CAMPAIGN",
    "INSERTION_ORDER",
    "LINE_ITEM",
]

FILE_TYPES_DICT = {
    "AD": "ads",
    "AD_GROUP": "adGroups",
    "CAMPAIGN": "campaigns",
    "LINE_ITEM": "lineItems",
    "INSERTION_ORDER": "insertionOrders",
}
