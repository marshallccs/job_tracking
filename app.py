import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import hmac

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from app_methods import Production

st.set_page_config(page_title="Job Tracking", page_icon="🌎", layout="wide")

job_production = Production()

task_adding = st.radio('Adding', options=['All Data', 'Add Task'], horizontal=True)

if task_adding == 'All Data':
    navigation_pane = st.radio(label='Navigation Pane', options=['Adhoc', 'Daily', 'Weekly', 'Monthly'], horizontal=True)
    if navigation_pane == 'Adhoc':
            job_production.display_data(displaytype=1, user_type=1)
    elif navigation_pane == 'Daily':
        job_production.display_data(displaytype=2, user_type=1)
    elif navigation_pane == 'Weekly':
        job_production.display_data(displaytype=3, user_type=1)
    elif navigation_pane == 'Monthly':
        job_production.display_data(displaytype=4, user_type=1)
elif task_adding == 'Add Task':
    job_production.add_job()