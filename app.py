import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from users import check_password
import pandas as pd

st.set_page_config(page_title="Task Tracking", layout="wide")
from app_methods import Production

# Check if the user is logged in
if check_password():
    # Hide the login form and display the main application content
    st.success(f"You are logged in! {st.session_state['logged_in_user']}")
    # Logout button to allow the user to log out
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["logged_in_user"] = None
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
else:
    # Stop the execution if not logged in, preventing app content from being shown
    st.stop()

job_production = Production()


# TODO: Check if the fullname will be needed in the creation for the data.

# User table
user_table = pd.read_csv('user_table.csv', encoding='latin-1', low_memory=False)

# User type
usertype = user_table.loc[user_table['username'] == st.session_state['logged_in_user'], 'usertype'].sum()

# Full name
fullname = user_table.loc[user_table['username'] == st.session_state['logged_in_user'], 'fullname'].sum()


job_production.display_data(user_type=usertype, full_name=fullname)

