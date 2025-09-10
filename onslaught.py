import streamlit as st
import pandas as pd
from gears import *

def onslaught():
    if "username" in st.session_state:

        initState()
        group1 = "onslaught_sessions"
        group2 = "onslaught_maps"
        
        account_id = st.session_state['account_id']

        t_onsl_l_1 = st.secrets["t_onsl_l_1"]
        t_onsl_l_2 = st.secrets["t_onsl_l_2"]

        t_onslT_l = st.secrets["t_onslT_l"]



        t_onsl_j = getJson(f"{t_onsl_l_1}{account_id}{t_onsl_l_2}")
        t_onsl_raw = pd.DataFrame(t_onsl_j["data"])

        # onslaught progression graph
        # we won't know what's inside until it starts...
        # t_onslT_j = getJson(f"{t_onslT_l}{account_id}")
        # t_onslT_raw = pd.DataFrame(t_onslT_j["data"])

        columnRename_dict = {
            'type': 'class',
            'is_premium': 'isPrem',
            'player_id': 'account_id',
        }
        onsl_cr = t_onsl_raw.rename(columns=columnRename_dict)
        onsl_cr['won'] = onsl_cr['won'].astype(int)

        # ========== battles list ==========
        reqCol_dict1 = ['map', 'geometry_name', 'spawn', 'won', 'battle_time',
                       'tank_id', 'short_name', 'nation', 'class', 'isPrem',
                       'damage', 'frags','base_xp', 'wn8', 'onslaught_delta',
                       'life_time', 'duration'
        ]
        onslS = onsl_cr[reqCol_dict1].copy()


        # ========== Efficiency by tanks ==========
        with st.expander(label="Efficiency"):
            data = onslS[['short_name', 'damage', 'frags','base_xp', 'wn8', 'onslaught_delta']]
            df = data.rename(columns={'short_name': 'name'})
            df[['damage', 'frags', 'base_xp', 'onslaught_delta']] = df[['damage', 'frags', 'base_xp', 'onslaught_delta']].apply(pd.to_numeric)

            st.subheader(f'Tank efficiency', help="Your most effective tanks", anchor=False)
            # number_input
            X = st.number_input(
                label="Minimum battles",
                min_value=0,
                value=10,
                step=1,
            )

            name_counts = df['name'].value_counts()
            valid_names = name_counts[name_counts >= X].index
            df_filtered = df[df['name'].isin(valid_names)]

            efficiency2 = df_filtered.groupby('name')['onslaught_delta'].mean().reset_index()
            efficiency2 = efficiency2.rename(columns={'onslaught_delta': 'x̄ Delta', 'name': 'Name'}).sort_values(by='x̄ Delta', ascending=False).round(2)
            
            correlation = df[['damage', 'frags', 'base_xp', 'onslaught_delta']].corr()
            correlation_colRename_dict = {
            'damage': 'Damage',
            'frags': 'Frags',
            'base_xp': 'XP',
            'onslaught_delta': 'x̄ Delta',
            }
            correlation_final = correlation.rename(columns=correlation_colRename_dict, inplace=True)
            correlation_final = correlation.rename(index=correlation_colRename_dict)
            
            st.dataframe(
                efficiency2,
                hide_index=True,
                height=215,
            )

            st.divider()
            
            st.subheader('Correlation', help="Impact on rating points", anchor=False)
            st.table(correlation_final['x̄ Delta'].sort_values(ascending=False).tail(3))

        st.subheader("Session statistics")
        # ========== FILTER1 ==========
        with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="center", gap="small"):
            applyFilter(onslS, "battle_time", group1, widget="dr")
            applyFilter(onslS, "short_name", group1, 'ms', ph="Tank name")
            applyFilter(onslS, "nation", group1, md=True)
            col1, col2 = st.columns(2, vertical_alignment="top")
            with col1:
                with st.container(border=False, width="stretch", horizontal_alignment="right", vertical_alignment="center", gap="small"):
                    applyFilter(onslS, "class", group1, md=True)
                    applyFilter(onslS, "map", group1, 'ms', ph="Map name")
        mask_onslS = get_filter_mask(onslS, group1)
        onslS_filtered = onslS.loc[mask_onslS].copy()
        # ===============================

        c1, c2, c3, c4, c5, c6, c7 = st.columns(7, gap="small", border=False, vertical_alignment="top", width='stretch')
        with c1:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="bottom", gap="small"):
                st.subheader("Battles", anchor=False, width="content")
                st.subheader(f"{len(onslS_filtered)}", anchor=False, width="content")
        with c2:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("WR%", anchor=False, width="content")
                st.subheader(f"{onslS_filtered[['won']].mean().item() * 100:.2f}", anchor=False, width="content")
        with c3:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("WN8", anchor=False, width="content")
                st.subheader(f"{onslS_filtered[['wn8']].mean().item():.0f}", anchor=False, width="content")
        with c4:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("Frags", anchor=False, width="content")
                st.subheader(f"{onslS_filtered[['frags']].mean().item():.1f}", anchor=False, width="content")
        with c5:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("XP", anchor=False, width="content")
                st.subheader(f"{onslS_filtered[['base_xp']].mean().item():.0f}", anchor=False, width="content")
        with c6:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("DMG", anchor=False, width="content")
                st.subheader(f"{onslS_filtered[['damage']].mean().item():.0f}", anchor=False, width="content")
        with c7:
            with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="top", gap="small"):
                st.subheader("RTNG", anchor=False, width="content", help="could be lie")
                st.subheader(f"{onslS_filtered[['onslaught_delta']].sum().item():.0f}", anchor=False, width="content")
        # ===============================

        def addIconColumnSp2(df, source_col, new_col, path, dep_col=None):
            '''Adds a new column with a markdown icon to df, special for onslaught table'''
            if source_col == 'geometry_name':
                df[new_col] = df[source_col].apply(lambda v: f"app/static/{path}/onslaught_{v}.png")
            else:
                df[new_col] = df[source_col].apply(lambda v: f"app/static/{path}/{v}.png")
            return df
        
        onslS_filtered = addIconColumnSp2(onslS_filtered, "geometry_name", "map_img", "geometry_name")
        onslS_filtered = addIconColumn(onslS_filtered, "nation", "nation_img", "nation")
        onslS_filtered = addIconColumn(onslS_filtered, "class", "class_img", "class", dep_col="isPrem")
        reqCol_dict2 = ['map_img', 'map', 'spawn', 'nation_img', 'class_img', 'short_name', 'damage', 'frags','base_xp', 'wn8', 'onslaught_delta', 'battle_time', 'won']
        onslS_filtered_final = onslS_filtered[reqCol_dict2]
        # =============================== 


        def highlight_row(row):
            if row['won'] == 1:
                color = "#1ae9070b"   # green
            else:
                color = "#dd13130c"   # red
            # including columns from the list
            styles = [''] * len(row)  
            for i, col in enumerate(row.index):
                if col in ['map_img', 'map', 'spawn', 'won']:
                    styles[i] = f'background-color: {color}'

            # # excluding columns from the list exclude_cols
            # styles = [f'background-color: {color}' if col not in 'wn8' else '' for col in row.index]
            return styles

        onslS_styled = (
            onslS_filtered_final
            .style
            .map(color_wn8, subset=['wn8'])
            .map(lambda x: 'color: green' if x == 1 else 'color: red', subset=['spawn'])
            .map(lambda x: 'color: red' if x < 0 else 'color: green', subset=['onslaught_delta'])
            .apply(highlight_row, axis=1)
            .format(precision=2)
        )

        # ===============================
        column_order = ['map_img', 'map', 'spawn', 'nation_img', 'class_img', 'short_name', 'damage', 'frags','base_xp', 'wn8', 'onslaught_delta', 'battle_time']
        onslaught_delta_help = "Install mod if None"
        column_config = {
            "map_img": st.column_config.ImageColumn(label="Map Image", width=50),
            "map": st.column_config.TextColumn(label="Map Name", width=75),
            "spawn": st.column_config.TextColumn(label="Spawn", width=30),
            "nation_img": st.column_config.ImageColumn(label="Nation", width=50),
            "class_img": st.column_config.ImageColumn(label="Class", width=30),
            "short_name": st.column_config.TextColumn(label="Name"),
            "damage": st.column_config.NumberColumn(label="DMG", width=50, format="localized"),
            "frags": st.column_config.NumberColumn(label="Frags", width=30),
            "base_xp": st.column_config.NumberColumn(label="XP", width=50),
            "wn8": st.column_config.NumberColumn(label="WN8", width=50, format="%.0f"),
            "onslaught_delta": st.column_config.NumberColumn(label="Delta", width=50, format="localized", help=onslaught_delta_help),
            "battle_time": st.column_config.DatetimeColumn(label="Date", width=50, format='DD.M.Y HH:mm'),
        }

        st.dataframe(
            data = onslS_styled,
            hide_index=True,
            column_order=column_order,
            column_config=column_config,
            height=350,
        )
        
        st.divider()
        # ========== MAPS ==========

        tmap = onslS_filtered[['map', 'geometry_name', 'spawn', 'won', 'damage', 'frags', 'wn8', 'life_time', 'duration', 'short_name']].copy()

        # Преобразование типов
        tmap['spawn'] = tmap['spawn'].astype(str)

        # Создание дополнительной колонки для группировки "Both"
        tmap['spawn_group'] = tmap['spawn'].replace(['1', '2'], 'Both')

        # Список колонок для агрегации
        agg_cols = ['won', 'damage', 'frags', 'wn8', 'life_time', 'duration']

        # Определяем словари агрегации для удобства
        agg_dict = {col: ('%s' % col, 'mean') for col in agg_cols}
        agg_dict['count'] = ('won', 'count')

        # Первая группировка по "spawn"
        tmap_grouped = tmap.groupby(['map', 'geometry_name', 'spawn'], as_index=False).agg(**agg_dict)

        # Вторая группировка по "Both"
        grouped_all = tmap.groupby(['map', 'geometry_name', 'spawn_group'], as_index=False).agg(**agg_dict)
        grouped_all.rename(columns={'spawn_group': 'spawn'}, inplace=True)

        # Объединяем результаты
        tmap_final = pd.concat([tmap_grouped, grouped_all], ignore_index=True)

        # Обработка данных
        tmap_final['won'] = (tmap_final['won'] * 100).round(2)
        for col in ['damage', 'frags', 'wn8', 'life_time', 'duration']:
            tmap_final[col] = tmap_final[col].round(2)

        # Выбор итоговых колонок
        reqColumns_dict = [
            'map', 'geometry_name', 'spawn', 'won',
            'damage', 'frags', 'wn8', 'life_time', 'duration', 'count',
        ]
        tmap_final = tmap_final[[col for col in reqColumns_dict if col in tmap_final.columns]]


        # ====== FILTER 2 ======
        # with st.container(border=True, width="stretch", horizontal_alignment="center", vertical_alignment="center", gap="small"):
            # col1, col2 = st.columns(2, vertical_alignment='center')
        # with col1:
        #     applyFilter(tmap_final, "map", group2, 'ms', ph= 'Map name')
        # with col2:
        #     applyFilter(tmap_final, "spawn", group2, 'sc')
        # st.button("Reset :material/Refresh:", on_click=lambda: resetFilters(group2), width="stretch")

        # mask_onslS = get_filter_mask(onslS, group1)
        # onslS_filtered = onslS.loc[mask_onslS].copy()

        # mask_map2 = get_filter_mask(tmap_final, group2)
        # tmap_final = tmap_final.loc[mask_map2].copy().reset_index()
        # =====================

        # ========== Add column Top3
        top_won_per_name = tmap.groupby(
            ['map', 'geometry_name', 'spawn', 'short_name']
        )['won'].mean().reset_index()

        top_3_names = (
            top_won_per_name
            .sort_values(by=['map','geometry_name','spawn','won'],
                        ascending=[True,True,True,False])
            .groupby(['map','geometry_name','spawn'])
            .head(3)
            .groupby(['map','geometry_name','spawn'])['short_name']
            .agg(', '.join)
            .reset_index()
            .rename(columns={'short_name':'Top3'})
        )

        top_3_names.rename(columns={'short_name': 'Top3'}, inplace=True)

        tmap_final = pd.merge(
            tmap_final, 
            top_3_names, 
            on=['map', 'geometry_name', 'spawn'], 
            how='left'
        )


        st.subheader(
            f"Map statistics / Loaded {len(tmap_final)} maps",
            help=f"Data collected for the period {str(onsl_cr['battle_time'].iloc[-1])[:10]} - {str(onsl_cr['battle_time'].iloc[0])[:10]}"
        )

        # ====== FILTER2 ======
        with col2:
            with st.container(border=False, width="stretch", horizontal_alignment="left", vertical_alignment="center", gap="small"):
                applyFilter(tmap_final, "spawn", group2, 'sc')
                st.button(":material/Refresh:", on_click=lambda: resetFilters(group1), width="stretch")

        mask_map = get_filter_mask(tmap_final, group2)
        tmap_final = tmap_final.loc[mask_map].copy().reset_index()
        # # =====================

        tmap_final = addIconColumnSp2(tmap_final, "geometry_name", "map_img", "geometry_name")
        tmap_final = addIconColumnSp2(tmap_final, "spawn", "spawn_img", "spawn")

        def color_cells(value):
            if value == '1':
                color = "#1ae9070b"
            elif value == '2':
                color =  "#dd13130c"
            else:
                color = ''

            return f'background-color: {color}'

        tmap_syled = (
                tmap_final
                .style
                .map(color_wn8, subset=['wn8'])
                .map(color_wr, subset=['won'])
                .map(color_cells, subset = ['spawn'])
                .format(precision=2)
        )
        

        column_order = ['map_img', 'map', 'spawn_img', 'count', 'won', 'wn8', 'damage', 'frags', 'life_time', 'duration', 'Top3']

        column_config = {
                "map_img": st.column_config.ImageColumn(label="Map Image", width=100),
                "map": st.column_config.TextColumn(label="Map Name", width=75),
                # "spawn": st.column_config.TextColumn(label="Spawn", width=50),
                "spawn_img": st.column_config.ImageColumn(label="Spawn", width=50),
                "count": st.column_config.NumberColumn(label="Battles", width=50),
                "won": st.column_config.NumberColumn(label="WR", width=50, format="%.2f"),
                "wn8": st.column_config.NumberColumn(label="WN8", width=50, format="%.0f"),
                "damage": st.column_config.NumberColumn(label="DMG", width=50, format="localized"),
                "frags": st.column_config.NumberColumn(label="Frags", width=50),
                "life_time": st.column_config.DatetimeColumn(label="Life Time (s)", width=50, format="%.0f"),
                "duration": st.column_config.NumberColumn(label="Duration (s)", width=50, format="%.0f"),
                "Top3": st.column_config.ListColumn(label="Top 3", width= 80, help="Top 3 most effective")
        }
        st.dataframe(
                data = tmap_syled,
                hide_index=True,
                column_order=column_order,
                row_height=100,
                column_config=column_config,
                height=790,
        )



        # ========== CHART raw ==========
        st.divider()
        st.warning("WORK IN PROGRESS")

        onslS_filtered_ch = onslS.copy()

        onslS_filtered_ch = (
            onslS_filtered_ch
            .sort_values(by='battle_time', ascending=True)
            .reset_index(drop=True)
        )
        onslS_filtered_ch['onslaught_delta_cumulative'] = (onslS_filtered_ch['onslaught_delta'].cumsum())

        st.line_chart(
            onslS_filtered_ch,
            x='battle_time',
            y='onslaught_delta_cumulative',
            x_label="Battle Time",
            y_label="Cumulative Delta",

        )
