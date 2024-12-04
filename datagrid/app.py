import json
import random
import base64
import streamlit as st

from .datatypes.utils import (
    get_color,
    get_rgb_from_hex,
    get_contrasting_color,
    generate_thumbnail,
    generate_image,
    download_data,
    image_to_fp,
    draw_annotations_on_image,
)
from .server.queries import (
    select_query_page,
    select_query_count,
    select_category,
    select_histogram,
    generate_chart_image,
    get_completions,
    verify_where,
)

IMAGE_SIZE = 200


def build_link(c, r, value):
    return """<a href="" id="%s,%s" style="color: black;">%s</a>""" % (c, r, value)


def format_text(value):
    if len(value) < 25:  ## and count_unique < 2000
        background = get_color(value)
        color = get_contrasting_color(background)
        value = f"""<div style="background: {background}; color: {color}; width: 80%; text-align: center; border-radius: 50px; margin-left: 10%;">{value}</div>"""
    return value


def build_header_row(column_names, width):
    retval = "<tr>"
    for name in column_names:
        retval += (
            """<th style="width: %spx; border: 1px solid; border-collapse: collapse; background-color: lightgray; padding-left: 10px;">%s</th>"""
            % (width, name)
        )
    retval += "</tr>"
    return retval


def build_row(DATAGRID, group_by, where, r, row, schema, experiment):
    retval = "<tr>"
    if group_by:
        max_height = 116
    else:
        max_height = 55
    for c, (column_name, value) in enumerate(row.items()):
        if group_by:
            if isinstance(value, dict):
                if value["type"] == "integer-group":
                    results = select_category(
                        DATAGRID,
                        group_by,
                        where=None,
                        column_name=column_name,
                        column_value=value["columnValue"],
                        where_description=None,
                        computed_columns=None,
                        where_expr=where,
                    )
                    if results["type"] == "category":
                        # st.write(results)
                        trace = {
                            "y": list(results["values"].keys()),
                            "x": list(results["values"].values()),
                            "marker": {
                                "color": [get_color(v) for v in results["values"]]
                            },
                        }
                        image_data = generate_chart_image(
                            results["type"], [trace], IMAGE_SIZE, IMAGE_SIZE
                        )
                        data = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                        value = (
                            """<img src="%s" style="max-height: %spx; width: 90%%"></img>"""
                            % (data, max_height)
                        )
                    elif results["type"] == "verbatim":
                        value = results["value"]

                elif value["type"] == "row-group":
                    # TODO
                    value = value["type"]

                elif value["type"] == "text-group":
                    # TODO
                    value = value["type"]

                elif value["type"] == "float-group":
                    results = select_histogram(
                        DATAGRID,
                        group_by,
                        where=None,
                        column_name=column_name,
                        column_value=value["columnValue"],
                        where_description=None,
                        computed_columns=None,
                        where_expr=where,
                    )
                    if results["type"] == "histogram":
                        # st.write(results)
                        trace = {
                            "x": results["labels"],
                            "y": results["bins"],
                            "marker": {"color": get_color(column_name)},
                        }
                        image_data = generate_chart_image(
                            results["type"], [trace], IMAGE_SIZE, IMAGE_SIZE
                        )
                        data = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                        value = (
                            """<img src="%s" style="max-height: %spx; width: 90%%"></img>"""
                            % (data, max_height)
                        )
                    elif results["type"] == "verbatim":
                        value = results["value"]

                elif value["type"] == "asset-group":
                    # TODO
                    value = value["type"]

                else:
                    raise Exception("Unknown group type: %r" % value["type"])
            else:
                value = format_text(value)
        else:
            # Non-grouped by row:
            # "INTEGER", "FLOAT", "BOOLEAN", "TEXT", "JSON"
            # "IMAGE-ASSET", "VIDEO-ASSET", "CURVE-ASSET", "ASSET-ASSET", "AUDIO-ASSET"
            if schema[column_name]["type"] == "IMAGE-ASSET":

                asset_data = experiment.get_asset(
                    value["assetData"]["asset_id"], return_type="binary"
                )

                bytes, image = generate_thumbnail(
                    asset_data,
                    annotations=value["assetData"]["annotations"],
                    return_image=True,
                )
                result = image_to_fp(image, "png").read()
                data = "data:image/png;base64," + base64.b64encode(result).decode(
                    "utf-8"
                )

                value = (
                    """<img src="%s" style="max-height: %spx; width: 90%%"></img>"""
                    % (data, max_height)
                )
            elif schema[column_name]["type"] == "TEXT":
                value = format_text(value)
            elif schema[column_name]["type"] == "INTEGER":
                pass
            elif schema[column_name]["type"] == "FLOAT":
                pass
            elif schema[column_name]["type"] == "BOOLEAN":
                value = format_text("True" if value else "False")
            elif schema[column_name]["type"] == "JSON":
                pass
            else:
                value = "Unsupported row render type: %s" % schema[column_name]["type"]

        if schema[column_name]["type"] not in ["ROW_ID"]:
            value = build_link(c, r, value)
        retval += (
            """<td style="border: 1px solid; border-collapse: collapse; text-align: center; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; height: %spx;">%s</td>"""
            % (max_height, value)
        )

    retval += "</tr>"
    return retval


def build_table(DATAGRID, group_by, where, data, schema, experiment, table_id):
    width = 200 if group_by else 150
    retval = f"""<table id="{table_id}" style="width: {len(data[0].keys()) * width}px; border: 1px solid; border-collapse: collapse; table-layout: fixed;">"""
    retval += build_header_row(data[0].keys(), width)
    for r, row in enumerate(data):
        retval += build_row(DATAGRID, group_by, where, r, row, schema, experiment)
    retval += "</table>"
    return retval, len(data[0].keys()) * width


@st.dialog("Image Viewer", width="large")
def render_image_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        st.write("TODO: image group")
    else:
        st.link_button(
            "Open image in tab",
            f"{BASEURL}/{experiment.workspace}/{experiment.project_name}/{experiment.id}?experiment-tab=images&graphicsAssetId={value['assetData']['asset_id']}",
        )
        columns = st.columns([1, 3])

        labels = columns[0].pills(
            "Labels:",
            sorted(value["assetData"]["labels"]),
            selection_mode="multi",
            default=value["assetData"]["labels"],
        )

        asset_data = experiment.get_asset(
            value["assetData"]["asset_id"], return_type="binary"
        )
        image = generate_image(asset_data)
        draw_annotations_on_image(
            image,
            value["assetData"]["annotations"],
            image.size[0],
            image.size[1],
            includes=labels,
        )

        columns[1].image(image)

    if st.button("Done", type="primary"):
        st.session_state["datagrid"]["table_id"] += 1
        st.rerun()


@st.dialog("Text Viewer", width="large")
def render_text_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        st.write("TODO: text group")
        # If too many, just show count
        # else show category plot
    else:
        st.write(value)

    if st.button("Done", type="primary"):
        st.session_state["datagrid"]["table_id"] += 1
        st.rerun()


@st.dialog("Integer Viewer", width="large")
def render_integer_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        st.write("TODO: integer group")
    else:
        st.write(value)

    if st.button("Done", type="primary"):
        st.session_state["datagrid"]["table_id"] += 1
        st.rerun()


@st.dialog("Float Viewer", width="large")
def render_float_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        st.write("TODO: float group")
    else:
        st.write(value)

    if st.button("Done", type="primary"):
        st.session_state["datagrid"]["table_id"] += 1
        st.rerun()


@st.dialog("Boolean Viewer", width="large")
def render_boolean_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        st.write("TODO: float group")
    else:
        st.write(value)

    if st.button("Done", type="primary"):
        st.session_state["datagrid"]["table_id"] += 1
        st.rerun()


@st.dialog("JSON Viewer", width="large")
def render_json_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        st.write("TODO: float group")
    else:
        st.json(value)

    if st.button("Done", type="primary"):
        st.session_state["datagrid"]["table_id"] += 1
        st.rerun()
