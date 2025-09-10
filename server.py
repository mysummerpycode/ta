import streamlit as st
import pandas as pd
from gears import *


def server():
    if "username" in st.session_state:
        
        initState()
        group = "server"

        build_id = getBuildId()

        # ========== server stat ==========
        t_sOverall_l_1 = st.secrets["t_sOverall_l_1"]
        t_sOverall_l_2 = st.secrets["t_sOverall_l_2"]

        t_sRecent_l_1 = st.secrets["t_sRecent_l_1"]
        t_sRecent_l_2 = st.secrets["t_sRecent_l_2"]

        t_sOverall_j = getJson(f"{t_sOverall_l_1}{build_id}{t_sOverall_l_2}")
        t_sRecent_j = getJson(f"{t_sRecent_l_1}{build_id}{t_sRecent_l_2}")

        t_sOverall_raw = pd.DataFrame(t_sOverall_j['pageProps']['overallData']['data'])
        t_sRecent_raw = pd.DataFrame(t_sRecent_j['pageProps']['data']['data'])


        # column rename
        t_sRecent_renDict = {
            'survival': 'survived',
            'base_xp': 'xp'
        }
        t_sRecent_renamed = t_sRecent_raw.rename(columns=t_sRecent_renDict)

        # choose your colunms
        t_sOverall_reqCol = ['tank_id', 'name', 'nation', 'tier', 'class', 'isPrem', 'battles', 'winrate', 'wn8', 'damage','frags', 'survived', 'hit_rate', 'spots', 'xp']
        t_sRecent_reqCol = t_sOverall_reqCol.copy()
        t_sRecent_reqCol.append('winrate_differential')


        t_sOverall = t_sOverall_raw[t_sOverall_reqCol]
        t_sRecent = t_sRecent_renamed[t_sRecent_reqCol]

        # ========== server economy ==========
        economics_l_1 = st.secrets["economics_l_1"]
        economics_l_2 = st.secrets["economics_l_2"]
        economics_j = getJson(f"{economics_l_1}{build_id}{economics_l_2}")
        economics_raw = pd.DataFrame(economics_j["pageProps"]["data"]["data"])
        economics = economics_raw.drop('image', axis=1)

        # ========== FILTERS ==========
        with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="center", gap="small"):
            applyFilter(t_sRecent, "name", group, 'ms', ph="Tank name")
            applyFilter(t_sRecent, "nation", group, md=True)
            applyFilter(t_sRecent, "tier", group, 'sc')
            applyFilter(t_sRecent, "class", group, md=True)
            applyFilter(t_sRecent, "isPrem", group, md=True)
            st.button(":material/Refresh:", on_click=lambda: resetFilters(group), width=96)


        mask_overall = get_filter_mask(t_sOverall, group)
        t_sOverall_filtered = t_sOverall.loc[mask_overall].copy()

        mask_recent = get_filter_mask(t_sRecent, group)
        t_sRecent_filtered = t_sRecent.loc[mask_recent].copy()

        mask_economics = get_filter_mask(economics, group)
        economics_filtered = economics.loc[mask_economics].copy()

        # ========== image to table ==========
        t_sOverall_filtered = addIconColumn(t_sOverall_filtered, "nation", "nation_img", "nation")
        t_sOverall_filtered = addIconColumn(t_sOverall_filtered, "class", "class_img", "class", dep_col="isPrem")

        t_sRecent_filtered = addIconColumn(t_sRecent_filtered, "nation", "nation_img", "nation")
        t_sRecent_filtered = addIconColumn(t_sRecent_filtered, "class", "class_img", "class", dep_col="isPrem")

        economics_filtered = addIconColumn(economics_filtered, "nation", "nation_img", "nation")
        economics_filtered = addIconColumn(economics_filtered, "class", "class_img", "class", dep_col="isPrem")


        # ========== color to cell ==========
        t_sOverall_styled = t_sOverall_filtered.style \
            .map(color_wn8, subset=['wn8']) \
            .map(color_wr, subset=['winrate'])
        t_sRecent_styled = t_sRecent_filtered.style \
            .map(color_wn8, subset=['wn8']) \
            .map(color_wr, subset=['winrate']) \
            .map(lambda x: 'color: red' if x < 0 else 'color: green', subset=['winrate_differential'])
        
        economics_styled = economics_filtered.style \
            .map(lambda x: 'color: red' if x < 0 else 'color: green', subset=['avg_profit']) \
            .map(lambda x: 'color: red' if x < 0 else 'color: green', subset=['profit_per_minute'])
        

        winrate_differential_help = "Values relative to the previous period"
        column_config={
            "nation_img": st.column_config.ImageColumn(label="Nation", width=50),
            "class_img": st.column_config.ImageColumn(label="Class", width=50),
            "tier": st.column_config.NumberColumn(label="Tier", width=40),
            "name": st.column_config.TextColumn(label="Name"),
            "battles": st.column_config.NumberColumn(label="Battles", width=50, format="localized"),
            "winrate": st.column_config.NumberColumn(label="WR", width=50, format="localized"),
            "wn8": st.column_config.NumberColumn(label="Wn8", width=50, format="localized"),
            "damage": st.column_config.NumberColumn(label="DMG", width=50, format="localized"),
            "frags": st.column_config.NumberColumn(label="Frags", width=50, format="localized"),
            "survived": st.column_config.NumberColumn(label="Survived", width=50, format="localized"),
            "hit_rate": st.column_config.NumberColumn(label="Hit%", width=50, format="localized"),
            "spots": st.column_config.NumberColumn(label="Spots", width=50, format="localized"),
            "xp": st.column_config.NumberColumn(label="XP", width=50, format="localized"),
            "winrate_differential": st.column_config.NumberColumn(label="WRdiff_s", width=50, format="localized", help=winrate_differential_help),
        }


        st.subheader(f"Server overall: {len(t_sOverall_filtered)} tanks", help=f"updated {t_sOverall_j['pageProps']['overallData']['meta']['updated'][:10]}")
        st.data_editor(
            t_sOverall_styled,
            height=350,
            hide_index=True,
            column_order=['nation_img', 'class_img', 'tier', 'name', 'battles', 'winrate',
                          'wn8', 'damage', 'frags', 'survived', 'hit_rate', 'spots', 'xp'],
            column_config=column_config,
            disabled=True,
            key='serverOverallStat'
        )

        st.subheader(f"Server recent: {len(t_sRecent_filtered)} tanks", help=f"updated {t_sRecent_j['pageProps']['data']['meta']['updated'][:10]}")
        st.data_editor(
            t_sRecent_styled,
            height=350,
            hide_index=True,
            column_order=['nation_img', 'class_img', 'tier', 'name', 'battles', 'winrate', 'winrate_differential', 
                          'wn8', 'damage', 'frags', 'survived', 'hit_rate', 'spots', 'xp'],
            column_config=column_config,
            disabled=True,
            key='serverRecentStat'
        )

        with st.expander(label=f"Tank Economics", expanded=True):
            st.data_editor(
                economics_styled,
                height=350,
                hide_index=True,
                column_order=['nation_img', 'class_img', 'tier', 'name', 'battles', 'avg_earnings', 'avg_profit','avg_ammo_cost',
                            'cost_per_shot', 'avg_repair_cost', 'avg_consumables_cost', 'earnings_per_minute', 'profit_per_minute'],
                column_config={
                    "nation_img": st.column_config.ImageColumn(label="Nation", width=50),
                    "class_img": st.column_config.ImageColumn(label="Class", width=50),
                    "tier": st.column_config.NumberColumn(label="Tier", width=40),
                    "name": st.column_config.TextColumn(label="Name"),
                    "battles": st.column_config.NumberColumn(label="Battles", width=50, format="localized"),
                    "avg_earnings": st.column_config.NumberColumn(label="x̄ Earn", width=50, format="localized"),
                    "avg_profit": st.column_config.NumberColumn(label="x̄ Profit", width=50, format="localized"),
                    "avg_ammo_cost": st.column_config.NumberColumn(label="x̄ Ammo Cost", width=50, format="localized"),
                    "cost_per_shot": st.column_config.NumberColumn(label="x̄ Cost/Shot", width=50, format="localized"),
                    "avg_repair_cost": st.column_config.NumberColumn(label="x̄ Repair", width=50, format="localized"),
                    "avg_consumables_cost": st.column_config.NumberColumn(label="x̄ Consumable", width=50, format="localized"),
                    "earnings_per_minute": st.column_config.NumberColumn(label="Earning/min", width=50, format="localized"),
                    "profit_per_minute": st.column_config.NumberColumn(label="Profit/min", width=50, format="localized"),
                },
                disabled=True,
                key='serverTankEconomics'
            )
            st.markdown(f"Minimum 100 battles", help=f"updated {economics_j['pageProps']['data']['meta']['updated'][:10]}")

        # # =========================
        # # What's the difference?
        # # =========================
        # merged_df = pd.merge(t_sOverall, t_sRecent, on='tank_id', how='left', indicator=True)
        # missingTanks_df = merged_df[merged_df['_merge'] == 'left_only'].drop(columns='_merge')

        # missingTanks_renDict = {old: new for old, new in zip(missingTanks_df, t_sOverall_reqCol)}
        # missingTanks_rennamed = missingTanks_df.rename(columns=missingTanks_renDict)
        # missingTanks = missingTanks_rennamed[t_sOverall_reqCol]

        # mask_missingTanks = get_filter_mask(missingTanks, group)
        # missingTanks_filtered = missingTanks.loc[mask_missingTanks].copy()

        # missingTanks_filtered = addIconColumn(missingTanks_filtered, "nation", "nation_img", "nation")
        # missingTanks_filtered = addIconColumn(missingTanks_filtered, "class", "class_img", "class", dep_col="isPrem")

        # missingTanks_styled = missingTanks_filtered.style \
        #     .map(color_wn8, subset=['wn8']) \
        #     .map(color_wr, subset=['winrate'])

        # with st.expander(label=f"What's the difference? {len(missingTanks)} tanks", expanded=False, width="stretch"):
        #     st.data_editor(
        #         missingTanks_styled,
        #         height=350,
        #         hide_index=True,
        #         column_order=['nation_img', 'class_img', 'tier', 'name', 'battles', 'winrate', 'wn8', 'damage', 'frags', 'survived', 'hit_rate', 'spots', 'xp'],
        #         column_config=column_config,
        #         disabled=True,
        #         key='missingTanks'
        #     )