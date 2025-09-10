import requests
import re
import streamlit as st
import pandas as pd

APP_ID = st.secrets["APP_ID"]
link = st.secrets["LINK"]

@st.cache_data(show_spinner=True)
def getUserCred(username: str):
    if not username:
        return None
    try:
        response = requests.get(f"{link}{username}")
        response.raise_for_status()
        data = response.json()

        if data["meta"]["count"] == 0 or not data["data"]:
            return None

        nickname = data["data"][0]["nickname"]
        account_id = data["data"][0]["account_id"]

        if not nickname or not account_id:
            return None

        return nickname, account_id

    except requests.exceptions.RequestException as e:
        st.toast(f"Error executing request: {e}")
        return None


def loginBlock():
    saved_username = st.query_params.get("u", "")
    saved_account_id = st.query_params.get("id", "")
    saved_page = st.query_params.get("p", "")

    if "username" not in st.session_state and saved_username:
        st.session_state["username"] = saved_username
    if "account_id" not in st.session_state and saved_account_id:
        st.session_state["account_id"] = saved_account_id

    # if authorized
    if "username" in st.session_state and "account_id" in st.session_state:
        st.header(f"`{st.session_state['username']}` `{st.session_state['account_id']}`")

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = saved_page if saved_page else "compare"
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            button_type_1 = "primary" if st.session_state["current_page"] == "compare" else "secondary"
            if st.button("P2S COMPARE", use_container_width=True, type=button_type_1):
                st.session_state["current_page"] = "compare"
                st.query_params["p"] = "compare"
                st.rerun()
        with col2:
            button_type_2 = "primary" if st.session_state["current_page"] == "maps" else "secondary"
            if st.button("MAPS", use_container_width=True, type=button_type_2):
                st.session_state["current_page"] = "maps"
                st.query_params["p"] = "maps"
                st.rerun()
        with col3:
            button_type_3 = "primary" if st.session_state["current_page"] == "moe" else "secondary"
            if st.button("MOE", use_container_width=True, type=button_type_3):
                st.session_state["current_page"] = "moe"
                st.query_params["p"] = "moe"
                st.rerun()
        with col4:
            button_type_4 = "primary" if st.session_state["current_page"] == "server" else "secondary"
            if st.button("SERVER", use_container_width=True, type=button_type_4):
                st.session_state["current_page"] = "server"
                st.query_params["p"] = "server"
                st.rerun()
        with col5:
            button_type_5 = "primary" if st.session_state["current_page"] == "onslaught" else "secondary"
            if st.button("ONSLAUGHT", use_container_width=True, type=button_type_5):
                st.session_state["current_page"] = "onslaught"
                st.query_params["p"] = "onslaught"
                st.rerun()
        
        if st.button(":material/Exit_To_App: Logout", use_container_width=True, type="secondary"):
            if "u" in st.query_params:
                del st.query_params["u"]
            if "id" in st.query_params:
                del st.query_params["id"]
            if "p" in st.query_params:
                del st.query_params["p"]

            st.session_state.pop("username", None)
            st.session_state.pop("account_id", None)
            st.session_state.pop("current_page", None)
            st.rerun()
        
        return True

    # login form
    username = st.text_input(
        label="Enter nickname",
        value=saved_username,
        placeholder="Enter your nickname",
        label_visibility="collapsed",
        key="username_input"
    )

    if username:
        user = getUserCred(username)
        if user:
            nickname, account_id = user
            st.session_state["username"] = nickname
            st.session_state["account_id"] = account_id
            st.query_params["u"] = nickname
            st.query_params["id"] = account_id
            st.rerun()
        else:
            st.error("❌ User not found")
    return False


@st.cache_data(show_spinner=True)
def getBuildId():
    try:
        response = requests.get(f"{st.secrets["tmain"]}")
        response.raise_for_status()
        data = response.text
        build_id = re.search(r'"buildId":"([^"]+)"', data)
        return build_id.group(1) if build_id else None
    
    except requests.exceptions.RequestException as e:
        st.toast(f"Error executing request: {e}")
        return None


@st.cache_data(show_spinner=True)
def getJson(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.toast(f"Error executing request: {e}")
        return None


@st.cache_data(show_spinner=True)
def addIconColumn(df, source_col, new_col, path, dep_col=None):
    """
    Adds a new column with a markdown icon to df.
    prem_col — if there is a dependency (e.g. class + isPrem).
    """
    if dep_col:
        df[new_col] = df.apply(
            lambda row: f"app/static/{path}/{'prem' if row[dep_col] else ''}{row[source_col]}.webp",
            axis=1
        )
    else:
        df[new_col] = df[source_col].apply(lambda v: f"app/static/{path}/{v}.webp")
    return df


# =========================
# cell color
# =========================
@st.cache_data(show_spinner=True)
def color_wn8(val):
    if pd.isna(val): return ''
    if val < 300: color = '#000000'
    elif val < 600: color = '#c93b35'
    elif val < 900: color = '#d27e14'
    elif val < 1250: color = '#d1ba1d'
    elif val < 1600: color = '#699728'
    elif val < 1900: color = '#4a7731'
    elif val < 2350: color = '#558fb6'
    elif val < 2900: color = '#85539c'
    else: color = '#5c2c74'
    return f'background-color: {color}'

@st.cache_data(show_spinner=True)
def color_wr(val):
    if pd.isna(val): return ''
    if val < 45: color = '#c93b35'
    elif val < 47: color = '#d27e14'
    elif val < 49: color = '#d1ba1d'
    elif val < 52: color = '#699728'
    elif val < 54: color = '#4a7731'
    elif val < 56: color = '#558fb6'
    elif val < 60: color = '#85539c'
    elif val < 65: color = '#5c2c74'
    else: color = "#55067d"
    return f'background-color: {color}'

# =============================================================================

def initState():
    """Initialization session_state."""
    initial_values = {
        "registered_filters": {},
        "filters": {},
        "reset_trigger": 0
    }
    for key, value in initial_values.items():
        st.session_state.setdefault(key, value)


def resetFilters(group: str):
    """Resets filters for the specified group.."""
    for key in st.session_state.registered_filters.get(group, {}):
        st.session_state.filters[key] = []
        if key in st.session_state:
            st.session_state[key] = []
    st.session_state.reset_trigger += 1


def getUniqueSortedValues(df, column):
    """Caches and returns sorted unique values."""
    values = df[column].dropna().unique()

    def sort_key(x):
        # numbers are sorted as numbers...
        if isinstance(x, (int, float)):
            return (0, x)
        # lines come after numbers
        return (1, str(x))

    return sorted(values, key=sort_key)


def applyFilter(df, column, group, widget='sc', md=False, lv="collapsed", ph=None, key=None):
    if key is None:
        key = f"{column}_{group}_{widget}"
    st.session_state.registered_filters.setdefault(group, {})[key] = column
    unique_vals = getUniqueSortedValues(df, column)

    st.session_state.filters.setdefault(key, [])

    # SERVER page, column "nation"
    # values are in lower case, but we need them in upper case
    # because of t_sOverall and t_sRecent. Fix this sometime...

    options = unique_vals
    selected = []

    if widget == 'sc':
        if md:
            options_dict = {
                f"![](app/static/{column}/{re.escape(str(v))}.webp)": v
                for v in unique_vals
            }
            options = list(options_dict.keys())
        
        selected = st.segmented_control(
            label=column,
            options=sorted(options),
            key=f"{key}_{st.session_state.reset_trigger}",
            selection_mode="multi",
            label_visibility=lv,
        )
        if md:
            st.session_state.filters[key] = [options_dict[s] for s in selected]
        else:
            st.session_state.filters[key] = selected
            
    elif widget == 'sb':
        options = ["All"] + unique_vals
        selected = st.selectbox(
            label=column,
            options=options,
            key=f"{key}_{st.session_state.reset_trigger}",
            label_visibility=lv,
            placeholder=ph
        )
        
        if selected == "All":
            st.session_state.filters[key] = []
        else:
            st.session_state.filters[key] = [selected]

    elif widget == 'ms':
        selected = st.multiselect(
            label=column,
            options=unique_vals,
            key=f"{key}_{st.session_state.reset_trigger}",
            label_visibility=lv,
            placeholder=ph
        )
        st.session_state.filters[key] = selected

    elif widget == "ss":
        min_val = 0
        max_val = max(unique_vals)

        selected = st.slider(
            label=column,
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            key=f"{key}_{st.session_state.reset_trigger}",
            label_visibility=lv,
        )
        st.session_state.filters[key] = selected
    
    elif widget == "dr":
        # сonvert column to datetime (preserving UTC)
        df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)

        min_date = df[column].min().to_pydatetime()
        max_date = df[column].max().to_pydatetime()

        # save as strings for session_state
        st.session_state.filters.setdefault(key, (str(min_date), str(max_date)))

        selected = st.slider(
            label=column,
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM-DD",
            key=f"{key}_{st.session_state.reset_trigger}",
            label_visibility=lv,
        )

        # put strings into the session, but return datetime
        st.session_state.filters[key] = (str(selected[0]), str(selected[1]))
        # return selected
        
    return st.session_state.filters[key]


def get_filter_mask(df, group):
    """General filter by group"""
    mask = pd.Series(True, index=df.index)
    for key, column in st.session_state.registered_filters.get(group, {}).items():
        filt = st.session_state.filters.get(key)

        if filt:
            # if range (slider)
            if isinstance(filt, tuple) and len(filt) == 2:
                mask &= df[column].between(filt[0], filt[1])
            # if list of values
            else:
                mask &= df[column].isin(filt)

    return mask