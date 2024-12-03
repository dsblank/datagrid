from .datatypes.utils import (
    get_color,
    get_rgb_from_hex,
    get_contrasting_color,
)
import json
import random

def build_header_row(column_names):
    retval = "<tr>"
    for name in column_names:
        retval += """<th style="width: 150px; border: 1px solid; border-collapse: collapse; background-color: lightgray; padding-left: 10px;">%s</th>""" % name
    retval += "</tr>"
    return retval

def build_row(r, row, schema, experiment_id):
    retval = "<tr>"
    for c, (column_name, value) in enumerate(row.items()):
        if schema[column_name]["type"] == "IMAGE-ASSET":
            json_data = json.loads(value.asset_id)
            value = """<a href="#" id="%s,%s"><img src="https://www.comet.com/api/asset/download?assetId=%s&experimentKey=%s" style="max-height: 55px;"></img></a>""" %  (c, r, json_data["asset_id"], experiment_id)
        elif schema[column_name]["type"] == "TEXT":
            if len(value) < 25: ## and count_unique < 2000
                background = get_color(value)
                color = get_contrasting_color(background)
                value = f"""<div style="background: {background}; color: {color}; width: 80%; text-align: center; border-radius: 50px; margin-left: 10%;">{value}</div>"""

        retval += """<td style="border: 1px solid; border-collapse: collapse; text-align: center; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; height: 55px;">%s</td>""" % value

    retval += "</tr>"
    return retval

def build_table(data, schema, experiment_id, table_id):
    width = len(data[0].keys()) * 150 if data else 100
    retval = f"""<table id="{table_id}" style="width: {width}px; border: 1px solid; border-collapse: collapse; table-layout: fixed;">"""
    retval += build_header_row(data[0].keys())
    for r, row in enumerate(data):
        retval += build_row(r, row, schema, experiment_id)
    retval += "</table>"
    return retval, width

