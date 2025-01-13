# -*- coding: utf-8 -*-
######################################################
#     _____                  _____      _     _      #
#    (____ \       _        |  ___)    (_)   | |     #
#     _   \ \ ____| |_  ____| | ___ ___ _  _ | |     #
#    | |  | )/ _  |  _)/ _  | |(_  / __) |/ || |     #
#    | |__/ ( ( | | | ( ( | | |__| | | | ( (_| |     #
#    |_____/ \_||_|___)\_||_|_____/|_| |_|\____|     #
#                                                    #
#    Copyright (c) 2023-2024 Kangas Development Team #
#    All rights reserved                             #
######################################################

import json
import random
import base64
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from ._datatypes.utils import (
    get_color,
    get_rgb_from_hex,
    get_contrasting_color,
    generate_thumbnail,
    generate_image,
    image_to_fp,
    draw_annotations_on_image,
    experiment_get_asset,
    THUMBNAIL_SIZE,
)
from .server.queries import (
    select_query_page,
    select_query_count,
    select_category,
    select_histogram,
    select_asset_group_thumbnail,
    select_asset_group,
    generate_chart_image,
    get_completions,
    verify_where,
    get_database_connection,
    select_group_by_rows,
)

IMAGE_SIZE = 200


def build_link(c, r, value):
    return """<a href="" id="%s,%s" style="color: black;">%s</a>""" % (c, r, value)


def format_text(value, width="80%"):
    if not isinstance(value, str):
        return value
    if len(value) < 25:  ## and count_unique < 2000
        background = get_color(value)
        color = get_contrasting_color(background)
        value = f"""<div style="background: {background}; color: {color}; width: {width}; text-align: center; border-radius: 50px; margin-left: 10%;">{value}</div>"""
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


def build_row(DATAGRID, group_by, where, r, row, schema, experiment, config):
    retval = "<tr>"
    if group_by:
        max_height = 116
    else:
        max_height = 55
    for c, (column_name, value) in enumerate(row.items()):
        linkable = True
        if group_by:
            if isinstance(value, dict):
                if value["type"] in ["integer-group", "text-group"]:
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
                        xy = sorted(
                            [(x, y) for x, y in results["values"].items()],
                            key=lambda item: item[0],
                        )
                        y = [v[0] for v in xy]
                        x = [v[1] for v in xy]

                        trace = {
                            "y": y,
                            "x": x,
                            "marker": {"color": [get_color(str(v)) for v in y]},
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
                        linkable = False

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
                        where=where,
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
                        linkable = False

                elif value["type"] == "asset-group":
                    image_data = select_asset_group_thumbnail(
                        experiment,
                        experiment.id,
                        DATAGRID,
                        group_by,
                        where=where,
                        column_name=column_name,
                        column_value=value["columnValue"],
                        column_offset=0,
                        computed_columns=None,
                        where_expr=where,
                        gallery_size=[3, 2],
                        background_color=(255, 255, 255),
                        image_size=(80, 50),
                        border_width=1,
                        distinct=True,
                    )
                    data = (
                        f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                    )
                    value = (
                        """<img src="%s" style="max-height: %spx; width: 100%%"></img>"""
                        % (
                            data,
                            max_height,
                        )
                    )
                else:
                    raise Exception("Unknown group type: %r" % value["type"])
            else:
                value = format_text(value)
                linkable = False
        else:
            # Non-grouped by row:
            # "INTEGER", "FLOAT", "BOOLEAN", "TEXT", "JSON"
            # "IMAGE-ASSET", "VIDEO-ASSET", "CURVE-ASSET", "ASSET-ASSET", "AUDIO-ASSET"
            if schema[column_name]["type"] == "IMAGE-ASSET":

                asset_data = experiment_get_asset(
                    experiment,
                    experiment.id,
                    value["assetData"]["asset_id"],
                    return_type="binary",
                )

                bytes, image = generate_thumbnail(
                    asset_data,
                    annotations=value["assetData"].get("annotations"),
                    return_image=True,
                )
                result = image_to_fp(image, "png").read()
                data = "data:image/png;base64," + base64.b64encode(result).decode(
                    "utf-8"
                )

                value = """<img src="%s" style="max-height: %spx;"></img>""" % (
                    data,
                    max_height,
                )
            elif schema[column_name]["type"] == "TEXT":
                value = format_text(value)
                linkable = False
            elif schema[column_name]["type"] == "INTEGER":
                if config["integer_separator"]:
                    value = "{:,}".format(value)
                linkable = False
            elif schema[column_name]["type"] == "FLOAT":
                if config["decimal_precision"] is not None:
                    expr = f"""%.0{config["decimal_precision"]}f"""
                    value = expr % value
                linkable = False
            elif schema[column_name]["type"] == "BOOLEAN":
                value = (
                    f"""<input type="checkbox" disabled {"checked" if value else ""}>"""
                )
                linkable = False
            elif schema[column_name]["type"] == "JSON":
                pass
            elif schema[column_name]["type"] == "ROW_ID":
                pass
            else:
                value = "Unsupported row render type: %s" % schema[column_name]["type"]

        if schema[column_name]["type"] not in ["ROW_ID"] and linkable:
            value = build_link(c, r, value)
        retval += (
            """<td style="border: 1px solid; border-collapse: collapse; text-align: center; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; height: %spx;">%s</td>"""
            % (max_height, value)
        )

    retval += "</tr>"
    return retval


# -webkit-fill-available
def build_table(DATAGRID, group_by, where, data, schema, experiment, table_id, config):
    width = 300 if group_by else 150
    retval = f"""<div style="display: block; width: -webkit-fill-available; overflow: auto;"><table id="{table_id}" style="width: {len(data[0].keys()) * width}px; border: 1px solid; border-collapse: collapse; table-layout: fixed;">"""
    retval += build_header_row(data[0].keys(), width)
    for r, row in enumerate(data):
        retval += build_row(
            DATAGRID, group_by, where, r, row, schema, experiment, config
        )
    retval += "</table></div>"
    return retval, len(data[0].keys()) * width


@st.dialog("Download DataGrid")
def render_download_dialog(BASEURL, dg, schema, where, experiment):
    use_urls = st.checkbox("Use Comet IDs for assets", value=True)
    include_metadata = st.checkbox(
        "Include asset metadata", value=True, disabled=use_urls
    )
    include_annotations = st.checkbox(
        "Include image annotations", value=True, disabled=use_urls
    )
    download_type = st.selectbox("Download format:", ["CSV", "JSON"])
    prepare = st.button("Prepare download")
    if prepare:
        data = dg.select(
            where=where,
            sort_by="row-id",
            select_columns=["row-id"] + dg.get_columns(),
            sort_desc=False,
            to_dicts=True,
            limit=None,
            offset=0,
        )
        if use_urls:
            for row in data:
                for column_name, column_value in row.items():
                    column_type = schema[column_name]["type"]
                    if column_type.endswith("-ASSET"):
                        row[column_name] = {
                            "assetId": column_value["assetData"]["asset_id"],
                            "experimentId": experiment.id,
                        }

        elif include_metadata is False or include_annotations is False:
            for row in data:
                for column_name, column_value in row.items():
                    column_type = schema[column_name]["type"]
                    if not include_metadata and column_type.endswith("-ASSET"):
                        if "metadata" in column_value["assetData"]:
                            del column_value["assetData"]["metadata"]
                    if not include_annotations and column_type == "IMAGE-ASSET":
                        if "annotations" in column_value["assetData"]:
                            del column_value["assetData"]["annotations"]
        if download_type == "CSV":
            df = pd.DataFrame(
                [list(row.values()) for row in data],
                columns=["row-id"] + dg.get_columns(),
            )
            df.set_index("row-id", inplace=True)
            formatted_data = df.to_csv().encode("utf-8")
            filename = "datagrid.csv"
        elif download_type == "JSON":
            formatted_data = json.dumps(data)
            filename = "datagrid.json"

        st.markdown(f"Length of selected data: {len(data)}")
        if st.download_button(
            "Download", formatted_data, file_name=filename, type="primary"
        ):
            st.rerun()


@st.dialog(" ", width="large")
def render_image_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        where_str = (" and %s" % value["whereExpr"]) if value["whereExpr"] else ""
        st.title(
            "Column %s, where %s == %r%s"
            % (value["columnName"], group_by, value["columnValue"], where_str)
        )
        results = select_asset_group(
            experiment,
            experiment.id,
            dgid=value["dgid"],
            group_by=value["groupBy"],
            where=value["whereExpr"],
            column_name=value["columnName"],
            column_value=value["columnValue"],
            column_offset=0,  # FIXME to allow paging of images
            column_limit=20,
            computed_columns=None,
            where_expr=value["whereExpr"],
            distinct=True,
        )
        data = [json.loads(item.replace("&comma;", ",")) for item in results["values"]]
        if len(data) < 20:
            st.write(
                f"Loading Total {len(data)} images in group; click image to open in tab"
            )
        else:
            st.write("Loading first 20 images in group; click image to open in tab")
        images = ""
        for i, value in enumerate(data):
            asset_data = experiment_get_asset(
                experiment, experiment.id, value["asset_id"], return_type="binary"
            )

            bytes, image = generate_thumbnail(
                asset_data,
                annotations=value.get("annotations"),
                return_image=True,
            )

            result = image_to_fp(image, "png").read()
            image_data = "data:image/png;base64," + base64.b64encode(result).decode(
                "utf-8"
            )

            url = f"{BASEURL}/{experiment.workspace}/{experiment.project_name}/{experiment.id}?experiment-tab=images&graphicsAssetId={value['asset_id']}"
            images += (
                """<a href="%s"><img src="%s" style="padding: 5px;"></img></a>"""
                % (url, image_data)
            )

        st.markdown(images, unsafe_allow_html=True)

    else:
        st.link_button(
            "Open image in tab",
            f"{BASEURL}/{experiment.workspace}/{experiment.project_name}/{experiment.id}?experiment-tab=images&graphicsAssetId={value['assetData']['asset_id']}",
        )
        columns = st.columns([1, 3])

        smooth = columns[0].checkbox("Smoothing", value=True)
        grayscale = columns[0].checkbox("Grayscale", value=False)
        labels_list = sorted(value["assetData"].get("labels", []))
        if labels_list:
            labels = columns[0].pills(
                "**Labels**:",
                labels_list,
                selection_mode="multi",
                default=labels_list,
            )

        if "metadata" in value["assetData"] and value["assetData"]["metadata"]:
            columns[0].markdown("**Image metadata**:")
            columns[0].json(value["assetData"]["metadata"])

        asset_data = experiment_get_asset(
            experiment,
            experiment.id,
            value["assetData"]["asset_id"],
            return_type="binary",
        )
        image = generate_image(asset_data)
        if grayscale:
            image = image.convert("L").convert("RGB")
        if "annotations" in value["assetData"]:
            draw_annotations_on_image(
                image,
                value["assetData"]["annotations"],
                image.size[0],
                image.size[1],
                includes=labels,
            )

        # columns[1].image(image, use_container_width=True)
        result = image_to_fp(image, "png").read()
        data = "data:image/png;base64," + base64.b64encode(result).decode("utf-8")

        value = f"""<img src="{data}" style="max-width: 100%; width: 500px; image-rendering: {"unset" if smooth else "pixelated"}; filter: "drop-shadow(2px 4px 6px black)";"></img>"""
        columns[1].html(value)
        # columns[1].image(image, use_container_width=True)

    if st.button("Done", type="primary"):
        st.session_state["table_id"] += 1
        st.rerun()


@st.dialog(" ", width="large")
def render_text_dialog(BASEURL, group_by, value, schema, experiment, callback):
    if group_by:
        if isinstance(value, dict):
            where_str = (" and %s" % value["whereExpr"]) if value["whereExpr"] else ""
            st.title(
                "Column %s, where %s == %r%s"
                % (value["columnName"], group_by, value["columnValue"], where_str)
            )
            st.markdown("Use **lasso** or **box** to select items in bars")
            results = select_category(
                value["dgid"],
                group_by,
                where=value["whereExpr"],
                column_name=value["columnName"],
                column_value=value["columnValue"],
                where_description=None,
                computed_columns=None,
                where_expr=value["whereExpr"],
            )
            if results["type"] == "category":
                layout = {
                    "showlegend": False,
                    "xaxis": {
                        "visible": True,
                        "showticklabels": True,
                    },
                    "yaxis": {
                        "visible": True,
                        "showticklabels": True,
                        "type": "category",
                    },
                }
                xy = sorted(
                    [(x, y) for x, y in results["values"].items()],
                    key=lambda item: item[0],
                )
                y = [v[0] for v in xy]
                x = [v[1] for v in xy]

                fig = go.Figure(
                    data=[
                        go.Bar(
                            y=y,
                            x=x,
                            marker_color=[get_color(v) for v in y],
                            orientation="h",
                        )
                    ]
                )
                fig.update_layout(**layout)
                event = st.plotly_chart(
                    fig,
                    on_select=lambda: callback(
                        "category_text",
                        value["columnName"],
                        group_by,
                        value["columnValue"],
                    ),
                    key="category_text",
                )
                if event["selection"]["points"]:
                    st.rerun()
        else:
            st.title("Text data")
            st.markdown(format_text(value, "100px"), unsafe_allow_html=True)
    else:
        st.title("Text data")
        st.markdown(format_text(value, "100px"), unsafe_allow_html=True)

    if st.button("Done", type="primary"):
        st.session_state["table_id"] += 1
        st.rerun()


@st.dialog(" ", width="large")
def render_integer_dialog(BASEURL, group_by, value, schema, experiment, callback):
    if group_by:
        if isinstance(value, dict):
            where_str = (" and %s" % value["whereExpr"]) if value["whereExpr"] else ""
            st.title(
                "Column %s, where %s == %r%s"
                % (value["columnName"], group_by, value["columnValue"], where_str)
            )
            st.markdown("Use **lasso** or **box** to select items in bars")
            results = select_category(
                value["dgid"],
                group_by,
                where=value["whereExpr"],
                column_name=value["columnName"],
                column_value=value["columnValue"],
                where_description=None,
                computed_columns=None,
                where_expr=value["whereExpr"],
            )
            if results["type"] == "category":
                layout = {
                    "showlegend": False,
                    "xaxis": {
                        "visible": True,
                        "showticklabels": True,
                    },
                    "yaxis": {
                        "visible": True,
                        "showticklabels": True,
                        "type": "category",
                    },
                }
                xy = sorted(
                    [(x, y) for x, y in results["values"].items()],
                    key=lambda item: item[0],
                )
                y = [v[0] for v in xy]
                x = [v[1] for v in xy]
                fig = go.Figure(
                    data=[
                        go.Bar(
                            y=y,
                            x=x,
                            marker_color=[get_color(str(v)) for v in y],
                            orientation="h",
                        )
                    ]
                )
                fig.update_layout(**layout)
                event = st.plotly_chart(
                    fig,
                    on_select=lambda: callback(
                        "category_integer",
                        value["columnName"],
                        group_by,
                        value["columnValue"],
                    ),
                    key="category_integer",
                )
                if event["selection"]["points"]:
                    st.rerun()
            elif results["type"] == "verbatim":
                value = results["value"]
        else:
            st.title("Integer data")
            st.write(value)
    else:
        st.title("Integer data")
        st.write(value)

    if st.button("Done", type="primary"):
        st.session_state["table_id"] += 1
        st.rerun()


@st.dialog(" ", width="large")
def render_float_dialog(BASEURL, group_by, value, schema, experiment, callback):
    if group_by:
        if isinstance(value, dict):
            where_str = (" and %s" % value["whereExpr"]) if value["whereExpr"] else ""
            st.title(
                "Column %s, where %s == %r%s"
                % (value["columnName"], group_by, value["columnValue"], where_str)
            )
            st.markdown("Use **lasso** or **box** to select items in bars")
            results = select_histogram(
                value["dgid"],
                group_by=group_by,
                where=value["whereExpr"],
                column_name=value["columnName"],
                column_value=value["columnValue"],
                where_description=None,
                computed_columns=None,
                where_expr=value["whereExpr"],
            )
            if results["type"] == "histogram":
                color = get_color(value["columnName"])
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=results["labels"],
                            y=results["bins"],
                            marker_color=color,
                        )
                    ]
                )
                columns = st.columns([2, 1])
                event = columns[0].plotly_chart(
                    fig,
                    key="histogram_float",
                    on_select=lambda: callback(
                        "histogram_float",
                        value["columnName"],
                        group_by,
                        value["columnValue"],
                        results["labels"],
                    ),
                )
                if event["selection"]["points"]:
                    st.rerun()

                columns[1].markdown("## Statistics")
                columns[1].markdown("**25%%**: %s" % results["statistics"]["25%"])
                columns[1].markdown("**50%%**: %s" % results["statistics"]["50%"])
                columns[1].markdown("**75%%**: %s" % results["statistics"]["75%"])
                columns[1].markdown("**count**: %s" % results["statistics"]["count"])
                columns[1].markdown("**max**: %s" % results["statistics"]["max"])
                columns[1].markdown("**mean**: %s" % results["statistics"]["mean"])
                columns[1].markdown("**median**: %s" % results["statistics"]["median"])
                columns[1].markdown("**min**: %s" % results["statistics"]["min"])
                columns[1].markdown("**std**: %s" % results["statistics"]["std"])
                columns[1].markdown("**sum**: %s" % results["statistics"]["sum"])

            elif results["type"] == "verbatim":
                value = results["value"]
                st.write(value)
        else:
            st.title("Float data")
            st.write(value)
    else:
        st.title("Float data")
        st.write(value)

    if st.button("Done", type="primary"):
        st.session_state["table_id"] += 1
        st.rerun()


@st.dialog(" ", width="large")
def render_boolean_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        if isinstance(value, dict):
            where_str = (" and %s" % value["whereExpr"]) if value["whereExpr"] else ""
            st.title(
                "Column %s, where %s == %r%s"
                % (value["columnName"], group_by, value["columnValue"], where_str)
            )
        else:
            st.title("Boolean data")

        st.write("TODO: boolean group")
    else:
        st.title("Boolean data")
        st.write(value)

    if st.button("Done", type="primary"):
        st.session_state["table_id"] += 1
        st.rerun()


@st.dialog(" ", width="large")
def render_json_dialog(BASEURL, group_by, value, schema, experiment):
    if group_by:
        if isinstance(value, dict):
            where_str = (" and %s" % value["whereExpr"]) if value["whereExpr"] else ""
            st.title(
                "Column %s, where %s == %r%s"
                % (value["columnName"], group_by, value["columnValue"], where_str)
            )
        else:
            st.title("JSON data")

        st.write("TODO: json group")
    else:
        st.title("JSON data")
        st.json(value)

    if st.button("Done", type="primary"):
        st.session_state["table_id"] += 1
        st.rerun()
