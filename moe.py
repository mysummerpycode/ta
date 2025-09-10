import streamlit as st
import json
import pandas as pd
from gears import *


def moe():
    if "username" in st.session_state:

        initState()
        group = "moe"
        
        account_id = st.session_state["account_id"]

        p_moe_l = st.secrets["p_moe_l"]
        mastery_l = st.secrets["mastery_l"]
        t_pOverall_l = st.secrets["t_pOverall_l"]

        p_moe_j = getJson(p_moe_l)
        p_moe_raw = p_moe_j["data"]["data"]
        p_moe_df = pd.DataFrame([{"id": rec["id"], **rec["marks"]}for rec in p_moe_raw])
        p_moe_df.rename(columns={"id": "tank_id",},inplace=True)

        mastery_j = getJson(mastery_l)
        mastery_raw = mastery_j["data"]["data"]
        mastery_raw = pd.DataFrame([{"id": rec["id"], **{f"mark_{i}": val for i, val in enumerate(rec["mastery"])}}for rec in mastery_raw])
        mastery_raw.rename(columns={"id": "tank_id"}, inplace=True)

        t_pOverall_j = getJson(f"{t_pOverall_l}{account_id}")
        t_pOverall_raw = pd.DataFrame(t_pOverall_j["data"]["tanks"])
        t_pOverall_raw.rename(columns={"id": "tank_id"}, inplace=True)
        

        pOverall_recCol_dict = [
            "tank_id",
            "name",
            "nation",
            "tier",
            "class",
            "isPrem",
            "moe",
            "mastery"
        ]
        t_pOverall_req = t_pOverall_raw[pOverall_recCol_dict]


        t_pOverall_req = t_pOverall_req.copy()

        moe_df = pd.merge(
            t_pOverall_req,
            p_moe_df,
            on="tank_id",
            how="inner",
        )

        mastery_df = pd.merge(
            t_pOverall_req,
            mastery_raw,
            on="tank_id",
            how="inner",
        )


        # Filters
        with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="center", gap="small"):
            applyFilter(moe_df, "name", group, "ms", ph="Tank name")
            applyFilter(moe_df, "nation", group, md=True)
            applyFilter(moe_df, "tier", group, "sc")
            col1, col2 = st.columns(2, vertical_alignment="top")
            with col1:
                with st.container(border=False, width="stretch", horizontal_alignment="right", vertical_alignment="center", gap="small"):
                    applyFilter(moe_df, "mastery", group, md=True)
                    applyFilter(moe_df, "isPrem", group, md=True)
            with col2:
                with st.container(border=False, width="stretch", horizontal_alignment="left", vertical_alignment="center", gap="small"):
                    applyFilter(moe_df, "class", group, md=True)
                    applyFilter(moe_df, "moe", group, md=True)
            st.button(":material/Refresh:", on_click=lambda: resetFilters(group), width=96)

        # Apply filter to the first table
        mask_overall = get_filter_mask(moe_df, group)
        moe_filtered = moe_df.loc[mask_overall].copy()
        # Apply filter to the second table
        mask_recent = get_filter_mask(mastery_df, group)
        mastery_filtered = mastery_df.loc[mask_recent].copy()


        moe_filtered = addIconColumn(moe_filtered, "nation", "nation_img", "nation")
        moe_filtered = addIconColumn(moe_filtered, "class", "class_img", "class", dep_col="isPrem")
        moe_filtered = addIconColumn(moe_filtered, "moe", "moe_img", "moe")

        mastery_filtered = addIconColumn(mastery_filtered, "nation", "nation_img", "nation")
        mastery_filtered = addIconColumn(mastery_filtered, "class", "class_img", "class", dep_col="isPrem")
        mastery_filtered = addIconColumn(mastery_filtered, "mastery", "mastery_img", "mastery")
        mastery_filtered = addIconColumn(mastery_filtered, "moe", "moe_img", "moe")


        st.header("Marks of Excellence requirements")
        st.data_editor(
            moe_filtered,
            height=350,
            hide_index=True,
            column_order=("nation_img", "class_img", "tier","name", "moe_img", "65", "85", "95"),
            column_config={
                "nation_img": st.column_config.ImageColumn(label="Nation", width=50),
                "class_img": st.column_config.ImageColumn(label="Class", width=50),
                "mastery_img": st.column_config.ImageColumn(label="Mastery", width=50),
                "moe_img": st.column_config.ImageColumn(label="MOE", width=50),
                "tier": st.column_config.NumberColumn(label="Tier", width=40),
                "name": st.column_config.TextColumn(label="Name"),
                "65": st.column_config.NumberColumn(label="65% /", width=50, format="localized"),
                "85": st.column_config.NumberColumn(label="85% //", width=50, format="localized"),
                "95": st.column_config.NumberColumn(label="95% ///", width=50, format="localized"),
            },
            disabled=True,
            key="moe_filtered"
        )


        st.header("Mastery requirements")
        st.data_editor(
            mastery_filtered,
            height=350,
            hide_index=True,
            column_order=("nation_img", "class_img", "tier","name", "mastery_img", "mark_0", "mark_1", "mark_2", "mark_3"),
            column_config={
                "nation_img": st.column_config.ImageColumn(label="Nation", width=50),
                "class_img": st.column_config.ImageColumn(label="Class", width=50),
                "mastery_img": st.column_config.ImageColumn(label="Mastery", width=50),
                "moe_img": st.column_config.ImageColumn(label="MOE", width=50),
                "tier": st.column_config.NumberColumn(label="Tier", width=40),
                "name": st.column_config.TextColumn(label="Name"),
                "mark_0": st.column_config.NumberColumn(label=f"1", width=50, format="localized"),
                "mark_1": st.column_config.NumberColumn(label="2", width=50, format="localized"),
                "mark_2": st.column_config.NumberColumn(label="3", width=50, format="localized"),
                "mark_3": st.column_config.NumberColumn(label="M", width=50, format="localized"),
            },
            disabled=True,
            key="mastery_filtered"
        )