import streamlit as st
import pandas as pd
from gears import *


def compare():
    if "username" in st.session_state:

        initState()
        group = "compare"

        account_id = st.session_state['account_id']

        build_id = getBuildId()

        t_sOverall_1 = st.secrets["t_sOverall_1"]
        t_sOverall_2 = st.secrets["t_sOverall_2"]
        t_sOverall_j = getJson(f"{t_sOverall_1}{build_id}{t_sOverall_2}")

        t_sRecent_1 = st.secrets["t_sRecent_1"]
        t_sRecent_2 = st.secrets["t_sRecent_2"]
        t_sRecent_j = getJson(f"{t_sRecent_1}{build_id}{t_sRecent_2}")

        t_pOverall_1 = st.secrets["t_pOverall_1"]
        t_pOverall_j = getJson(f"{t_pOverall_1}{account_id}")

        t_sOverall_raw = pd.DataFrame(t_sOverall_j['pageProps']['overallData']['data'])
        t_sRecent_raw = pd.DataFrame(t_sRecent_j['pageProps']['data']['data'])
        t_pOverall_raw = pd.DataFrame(t_pOverall_j['data']['tanks'])
        t_pOverall_raw.rename(columns={'id': 'tank_id'}, inplace=True)

        # ========================
        c1, c2, c3, c4, c5 = st.columns(5, gap="small", border=False, vertical_alignment="top", width='stretch')
        with c1:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="bottom", gap="small"):
                st.subheader("Battles", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['battles'], anchor=False, width="content")
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("Frags", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['frags'], anchor=False, width="content")
        with c2:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("WR%", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['winrate'], anchor=False, width="content")
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("Assist", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['assist'], anchor=False, width="content")
        with c3:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("WNX", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['overallWNX'], anchor=False, width="content")
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("XP", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['xp'], anchor=False, width="content")
        with c4:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("WN8", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['overallWN8'], anchor=False, width="content")
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("Survival", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['survival'], anchor=False, width="content")
        with c5:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("DMG", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['dpg'], anchor=False, width="content")
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("K/D", anchor=False, width="content")
                st.subheader(t_pOverall_j['data']['kd'], anchor=False, width="content")
        # ========================
        cOverall_raw = pd.merge(
            t_pOverall_raw,
            t_sOverall_raw,
            on='tank_id',
            how='inner',
            suffixes=('_p', '_s')
        )

        cRecent_raw = pd.merge(
            t_pOverall_raw,
            t_sRecent_raw,
            on='tank_id',
            how='inner',
            suffixes=('_p', '_s')
        )
        # ========================

        # choose your colunms
        reqColumns_dict = [
            'tank_id',
            'name_p',
            'nation_p',
            'tier_p',
            'class_p',
            'isPrem_p',
            'battles_p',
            'winrate_p',
            'wn8_p',
            'dpg',
            'moe',
            'mastery',
            'battles_s',
            'winrate_s',
            'wn8_s',
            'damage'
        ]
        cOverall_req = cOverall_raw[reqColumns_dict]

        reqColumns_recent = reqColumns_dict.copy()
        reqColumns_recent.append('winrate_differential')
        cRecent_req = cRecent_raw[reqColumns_recent]

        # column rename
        rename_dict = {
            'name_p': 'name',
            'nation_p': 'nation',
            'tier_p': 'tier',
            'class_p': 'class',
            'isPrem_p': 'isPrem',
            'dpg': 'dpg_p',
            'damage': 'dpg_s',
        }
        cOverall = cOverall_req.rename(columns=rename_dict)
        cRecent = cRecent_req.rename(columns=rename_dict)

        # Filters
        with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="center", gap="small"):
            applyFilter(cOverall, "battles_p", group, 'ss')
            applyFilter(cOverall, "name", group, 'ms', ph="Tank name")
            applyFilter(cOverall, "nation", group, md=True)
            applyFilter(cOverall, "tier", group, 'sc')
            col1, col2 = st.columns(2, vertical_alignment="top")
            with col1:
                with st.container(border=False, width="stretch", horizontal_alignment="right", vertical_alignment="center", gap="small"):
                    applyFilter(cOverall, "mastery", group, md=True)
                    applyFilter(cOverall, "isPrem", group, md=True)
            with col2:
                with st.container(border=False, width="stretch", horizontal_alignment="left", vertical_alignment="center", gap="small"):
                    applyFilter(cOverall, "class", group, md=True)
                    applyFilter(cOverall, "moe", group, md=True)
            st.button(":material/Refresh:", on_click=lambda: resetFilters(group), width=96)

        # Apply filter to the first table
        mask_overall = get_filter_mask(cOverall, group)
        t_sOverall_filtered = cOverall.loc[mask_overall].copy()
        # Apply filter to the second table
        mask_recent = get_filter_mask(cRecent, group)
        t_sRecent_filtered = cRecent.loc[mask_recent].copy()
        # ========================

        # Adding icons
        t_sOverall_filtered = addIconColumn(t_sOverall_filtered, "nation", "nation_img", "nation")
        t_sOverall_filtered = addIconColumn(t_sOverall_filtered, "class", "class_img", "class", dep_col="isPrem")
        t_sOverall_filtered = addIconColumn(t_sOverall_filtered, "mastery", "mastery_img", "mastery")
        t_sOverall_filtered = addIconColumn(t_sOverall_filtered, "moe", "moe_img", "moe")

        t_sRecent_filtered = addIconColumn(t_sRecent_filtered, "nation", "nation_img", "nation")
        t_sRecent_filtered = addIconColumn(t_sRecent_filtered, "class", "class_img", "class", dep_col="isPrem")
        t_sRecent_filtered = addIconColumn(t_sRecent_filtered, "mastery", "mastery_img", "mastery")
        t_sRecent_filtered = addIconColumn(t_sRecent_filtered, "moe", "moe_img", "moe")

        # Stylization
        t_sOverall_styled = t_sOverall_filtered.style \
            .map(color_wn8, subset=['wn8_p', 'wn8_s']) \
            .map(color_wr, subset=['winrate_p', 'winrate_s'])
        t_sRecent_styled = t_sRecent_filtered.style \
            .map(color_wn8, subset=['wn8_p', 'wn8_s']) \
            .map(color_wr, subset=['winrate_p', 'winrate_s']) \
            .map(lambda x: 'color: red' if x < 0 else 'color: green', subset=['winrate_differential'])

        # ========================
        column_order = [
            "nation_img",
            "class_img",
            "tier",
            "name",
            "battles_p",
            "winrate_p", 
            "wn8_p",
            'dpg_p',
            'moe_img',
            "mastery_img",
            "battles_s",
            "winrate_s",
            "winrate_differential",
            "wn8_s",
            'dpg_s'
        ]

        winrate_differential_help = "Values relative to the previous period"
        column_config = {
            "nation_img": st.column_config.ImageColumn(label="Nation", width=50),
            "class_img": st.column_config.ImageColumn(label="Class", width=50),
            "tier": st.column_config.NumberColumn(label="Tier", width=40),
            "name": st.column_config.TextColumn(label="Name"),
            "battles_p": st.column_config.NumberColumn(label="Battles_p", width=50, format="localized"),
            "winrate_p": st.column_config.NumberColumn(label="WR_p", width=50, format="localized"),
            "wn8_p": st.column_config.NumberColumn(label="WN8_p", width=50, format="localized"),
            "dpg_p": st.column_config.NumberColumn(label="DMG_p", width=50, format="localized"),
            "moe_img": st.column_config.ImageColumn(label="MOE", width=50),
            "mastery_img": st.column_config.ImageColumn(label="Mastery", width=50),
            "battles_s": st.column_config.NumberColumn(label="Battles_s", width=50, format="localized"),
            "winrate_s": st.column_config.NumberColumn(label="WR_s", width=50, format="localized"),
            "winrate_differential": st.column_config.NumberColumn(label="WRdiff_s", width=50, format="localized", help=winrate_differential_help),
            "wn8_s": st.column_config.NumberColumn(label="WN8_s", width=50, format="localized"),
            "dpg_s": st.column_config.NumberColumn(label="DMG_s", width=50, format="localized"),
        }

        st.subheader(f"Server recent: {len(t_sRecent_filtered)} tanks", help=f"updated {t_sRecent_j['pageProps']['data']['meta']['updated'][:10]}")
        st.data_editor(
            t_sRecent_styled,
            height=350,
            hide_index=True,
            column_order=column_order,
            column_config=column_config,
            disabled=True,
            key='p2sRecent'
        )

        st.subheader(f"Server overall: {len(t_sOverall_filtered)} tanks", help=f"updated {t_sOverall_j['pageProps']['overallData']['meta']['updated'][:10]}")
        st.data_editor(
            t_sOverall_styled,
            height=350,
            hide_index=True,
            column_order=column_order,
            column_config=column_config,
            disabled=True,
            key='p2sOverall'
        )

        table1 = cOverall['name'].unique().tolist()
        table2 = cRecent['name'].unique().tolist()
        difference1 = [item for item in table1 if item not in table2]
        

        st.markdown(f" #### overall <=> recent: {difference1}")
        
        st.markdown("![](app/static/class/TD.webp)")