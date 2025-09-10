import streamlit as st
import pandas as pd
from gears import *


def maps():
    if "username" in st.session_state:

        initState()
        group1 = "maps_tankF"
        group2 = "maps_mapF"
        
        account_id = st.session_state['account_id']
        t_pmap_l_1 = st.secrets["t_pmap_l_1"]
        t_pmap_l_2 = st.secrets["t_pmap_l_2"]
        t_pmap_j = getJson(f"{t_pmap_l_1}{account_id}{t_pmap_l_2}")
        t_pmap_raw = pd.DataFrame(t_pmap_j["data"])

        # column rename
        columnRename_dict = {
            'type': 'class',
            'is_premium': 'isPrem',
            'player_id': 'account_id',
            'arena_gui': 'battleType'
        }
        t_pmap_cr = t_pmap_raw.rename(columns=columnRename_dict)

        # column val rename
        valRename_dict = {
            1: "Random",
            29: "Fun Random",
            21: "Frontline",
            30: "Onslaught",
            15: "Strongholds",
            16: "Clan Wars",
            19: "Grand Battle",
            2: "Training",
        }
        t_pmap_cr['battleType'] = t_pmap_cr['battleType'].map(valRename_dict)

        tmap = t_pmap_cr[['map', 'geometry_name', 'battleType', 'spawn', 'won',
                          'tank_id', 'short_name', 'nation', 'class', 'tier', 'isPrem',
                          'damage', 'frags', 'wn8', 'life_time', 'duration', 'battle_time', 'base_xp']].copy()

        # Преобразование типов
        tmap['won'] = tmap['won'].astype(int)
        tmap['spawn'] = tmap['spawn'].astype(str)

        # ====== FILTER 1======
        container = st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="center", gap="small")
        with container:
            applyFilter(tmap, "battle_time", group1, widget="dr")
            applyFilter(tmap, "short_name", group1, 'ms', ph="Tank name")
            applyFilter(tmap, "nation", group1, md=True)
            applyFilter(tmap, "tier", group1)
            col1, col2 = st.columns(2, vertical_alignment="center")
            with col1:
                with st.container(border=False, width="stretch", horizontal_alignment="right", vertical_alignment="center", gap="small"):
                    applyFilter(tmap, "class", group1, md=True)
            with col2:
                with st.container(border=False, width="stretch", horizontal_alignment="left", vertical_alignment="center", gap="small"):
                    applyFilter(tmap, "isPrem", group1, md=True)


        mask_map1 = get_filter_mask(tmap, group1)
        tmap = tmap.loc[mask_map1].copy().reset_index()
        # ============

        tmap['spawn_group'] = tmap['spawn'].replace(['1', '2'], 'Both')
        agg_cols = ['won', 'damage', 'frags', 'wn8', 'life_time', 'duration']
        agg_dict = {col: ('%s' % col, 'mean') for col in agg_cols}
        agg_dict['count'] = ('won', 'count')

        tmap_grouped = tmap.groupby(['map', 'geometry_name', 'battleType', 'spawn'], as_index=False).agg(**agg_dict)

        grouped_all = tmap.groupby(['map', 'geometry_name', 'battleType', 'spawn_group'], as_index=False).agg(**agg_dict)
        grouped_all.rename(columns={'spawn_group': 'spawn'}, inplace=True)

        tmap_final = pd.concat([tmap_grouped, grouped_all], ignore_index=True)

        tmap_final['won'] = (tmap_final['won'] * 100).round(2)
        for col in ['damage', 'frags', 'wn8', 'life_time', 'duration']:
            tmap_final[col] = tmap_final[col].round(2)


        reqColumns_dict = [
            'map', 'geometry_name', 'battleType', 'spawn', 'won',
            'damage', 'frags', 'wn8', 'life_time', 'duration', 'count'
        ]
        tmap_final = tmap_final[[col for col in reqColumns_dict if col in tmap_final.columns]]

        # ====== Top3 ======
        top_won_per_name = tmap.groupby(
            ['map', 'geometry_name', 'battleType', 'spawn', 'short_name']
        )['won'].mean().reset_index()

        top_3_names = (
            top_won_per_name
            .sort_values(by=['map','geometry_name','battleType','spawn','won'],
                        ascending=[True,True,True,True,False])
            .groupby(['map','geometry_name','battleType','spawn'])
            .head(3)
            .groupby(['map','geometry_name','battleType','spawn'])['short_name']
            .agg(', '.join)
            .reset_index()
            .rename(columns={'short_name':'Top3'})
        )

        top_3_names.rename(columns={'short_name': 'Top3'}, inplace=True)
        # ============

        tmap_final = pd.merge(
            tmap_final, 
            top_3_names, 
            on=['map', 'geometry_name', 'battleType', 'spawn'], 
            how='left'
        )

        # ====== FILTER 2 ======
        with container:
            with col1:
                with st.container(border=False, width="stretch", horizontal_alignment="right", vertical_alignment="center", gap="small"):
                    applyFilter(tmap_final, "battleType", group2, 'ms', ph="Battle type")
                    applyFilter(tmap_final, "map", group2, 'ms', ph="Map name")
            with col2:
                with st.container(border=False, width="stretch", horizontal_alignment="left", vertical_alignment="center", gap="small"):
                    applyFilter(tmap_final, "spawn", group2, 'sc')
                    st.button("Reset :material/Refresh:", on_click=lambda: resetFilters(group2), width="stretch")
        mask_map2 = get_filter_mask(tmap_final, group2)
        tmap_final = tmap_final.loc[mask_map2].copy().reset_index()
        # ============

        # c1, c2, c3, c4, c5, c6 = st.columns(6, gap="small", border=False, vertical_alignment="top", width='stretch')
        # with c1:
        #     with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="bottom", gap="small"):
        #         st.subheader("Batles", anchor=False, width="content")
        #         st.subheader(f"{len(tmap)}", anchor=False, width="content")
        # with c2:
        #     with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
        #         st.subheader("WR%", anchor=False, width="content")
        #         st.subheader(f"{tmap_final[['won']].mean().item() * 100:.2f}", anchor=False, width="content")
        # with c3:
        #     with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
        #         st.subheader("WN8", anchor=False, width="content")
        #         st.subheader(f"{tmap_final[['wn8']].mean().item():.0f}", anchor=False, width="content")
        # with c4:
        #     with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
        #         st.subheader("Frags", anchor=False, width="content")
        #         st.subheader(f"{tmap_final[['frags']].mean().item():.1f}", anchor=False, width="content")
        # with c5:
        #     with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
        #         st.subheader("XP", anchor=False, width="content")
        #         st.subheader(f"{tmap_final[['base_xp']].mean().item():.0f}", anchor=False, width="content")
        # with c6:
        #     with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
        #         st.subheader("DMG", anchor=False, width="content")
        #         st.subheader(f"{tmap_final[['damage']].mean().item():.0f}", anchor=False, width="content")
        # # ============

        def addIconColumnSp1(df, source_col, new_col, path, dep_col=None, pref1=None, pref2=None, excl=None):
            """
            Adds a new column with a markdown icon to df.
            """
            if dep_col:
                df[new_col] = df.apply(
                    lambda row: f"app/static/{path}/"
                                f"{pref1 if row[dep_col] != excl else pref2}"
                                f"{row[source_col]}.png",
                    axis=1
                )
            else:
                df[new_col] = df[source_col].apply(lambda v: f"app/static/{path}/{v}.png")

            return df


        tmap_final = addIconColumnSp1(
            df = tmap_final,
            source_col='geometry_name',
            new_col='map_img',
            path='geometry_name',
            dep_col='battleType',
            pref1='standard_',
            pref2='onslaught_',
            excl='Onslaught'
        )
        tmap_final = addIconColumnSp1(tmap_final, "spawn", "spawn_img", "spawn")

        def color_cells(value):
            if value == '1':
                color = "#1ae9072a"
            elif value == '2':
                color = "#dd13132b"
            else:
                color = ''

            return f'background-color: {color}'

        tmap_syled = (
                tmap_final
                .style
                .map(color_wn8, subset=['wn8'])
                .map(color_wr, subset=['won'])
                # .map(color_cells, subset = ['spawn'])
                .format(precision=2)
        )
        

        column_order = ['map_img', 'map', 'battleType', 'spawn_img', 'count', 'won', 'wn8', 'damage', 'frags', 'life_time', 'duration', 'Top3']

        column_config = {
                "map_img": st.column_config.ImageColumn(label="Map Image", width=100),
                "map": st.column_config.TextColumn(label="Map Name", width=75),
                "battleType'": st.column_config.TextColumn(label="Battle type", width=50),
                "spawn": st.column_config.TextColumn(label="Spawn", width=50),
                "spawn_img": st.column_config.ImageColumn(label="Spawn", width=50),
                "count": st.column_config.NumberColumn(label="Battles", width=50),
                "won": st.column_config.NumberColumn(label="WR", width=50, format="%.2f"),
                "wn8": st.column_config.NumberColumn(label="WN8", width=50, format="%.0f"),
                "damage": st.column_config.NumberColumn(label="DMG", width=50, format="localized"),
                "frags": st.column_config.NumberColumn(label="Frags", width=50),
                "life_time": st.column_config.NumberColumn(label="Life Time (s)", width=50, format="%.0f"),
                "duration": st.column_config.NumberColumn(label="Duration (s)", width=50, format="%.0f"),
                "Top3": st.column_config.ListColumn(label="Top 3", width= 80, help="Top 3 most effective")
        }
        st.subheader(
            f"Loaded {len(tmap_final)} maps",
            help=f"Data collected for the period {str(t_pmap_cr['battle_time'].iloc[-1])[:10]} - {str(t_pmap_cr['battle_time'].iloc[0])[:10]}"
        )
        st.dataframe(
                data = tmap_syled,
                hide_index=True,
                column_order=column_order,
                row_height=100,
                column_config=column_config,
                height=790,
        )
