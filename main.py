import streamlit as st
from gears import *
from compare import *
from maps import *
from moe import *
from server import *
from onslaught import *


st.set_page_config(page_title="tmtAddon", layout="wide", page_icon=":frog:")


def main():
    initState()
    auth_status = loginBlock()
    if auth_status:
        page = st.session_state.get("current_page", "compare_p")
        if page == "compare":
            compare()
        elif page == "maps":
            maps()
        elif page == "moe":
            moe()
        elif page == "server":
            server()
        elif page == "onslaught":
            onslaught()
        else:
            st.error("⚠️ Page not found.")
    else:
        st.info("Enter a player's name in the field above")
    


if __name__ == "__main__":

    main()
