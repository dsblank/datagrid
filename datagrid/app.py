from .datatypes.utils import (
    get_color,
    get_rgb_from_hex,
    get_contrasting_color,
    generate_thumbnail,
    download_data,
    image_to_fp,
)
import json
import random
import base64

def build_header_row(column_names):
    retval = "<tr>"
    for name in column_names:
        retval += """<th style="width: 150px; border: 1px solid; border-collapse: collapse; background-color: lightgray; padding-left: 10px;">%s</th>""" % name
    retval += "</tr>"
    return retval

def build_row(r, row, schema, experiment):
    retval = "<tr>"
    for c, (column_name, value) in enumerate(row.items()):
        if schema[column_name]["type"] == "IMAGE-ASSET":

            asset_data = experiment.get_asset(value["assetData"]["asset_id"], return_type="binary")
            
            bytes, image = generate_thumbnail(
                asset_data, annotations=value["assetData"]["annotations"], return_image=True
            )
            result = image_to_fp(image, "png").read()
            data = "data:image/png;base64," + base64.b64encode(result).decode("utf-8")

            
            value = """<img src="%s" style="max-height: 55px;"></img>""" %  data
        elif schema[column_name]["type"] == "TEXT":
            if len(value) < 25: ## and count_unique < 2000
                background = get_color(value)
                color = get_contrasting_color(background)
                value = f"""<div style="background: {background}; color: {color}; width: 80%; text-align: center; border-radius: 50px; margin-left: 10%;">{value}</div>"""

        retval += """<td style="border: 1px solid; border-collapse: collapse; text-align: center; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; height: 55px;"><a href="#" id="%s,%s" style="color: black;">%s</a></td>""" % (c, r, value)

    retval += "</tr>"
    return retval

def build_table(data, schema, experiment, table_id):
    width = len(data[0].keys()) * 150 if data else 100
    retval = f"""<table id="{table_id}" style="width: {width}px; border: 1px solid; border-collapse: collapse; table-layout: fixed;">"""
    retval += build_header_row(data[0].keys())
    for r, row in enumerate(data):
        retval += build_row(r, row, schema, experiment)
    retval += "</table>"
    return retval, width

