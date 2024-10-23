# def check_password():
#     """Returns `True` if the user has entered a correct password."""

#     def login_form():
#         """Form with widgets to collect user information"""
#         with st.form("Credentials"):
#             st.text_input("Username", key="username")
#             st.text_input("Password", type="password", key="password")
#             st.form_submit_button("Log in", on_click=password_entered)

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if st.session_state["username"] in st.secrets[
#             "passwords"
#         ] and hmac.compare_digest(
#             st.session_state["password"],
#             st.secrets.passwords[st.session_state["username"]],
#         ):
#             st.session_state["password_correct"] = True
#             st.session_state["logged_in"] = True  # Set logged_in state
#             st.session_state["logged_in_user"] = st.session_state["username"]
#             del st.session_state["password"]  # Don't store the password
#         else:
#             st.session_state["password_correct"] = False

#     # Check if the user is already logged in
#     if st.session_state.get("logged_in", False):
#         return True

#     # If not logged in, display the login form
#     login_form()

#     if "password_correct" in st.session_state:
#         if not st.session_state["password_correct"]:
#             st.error("😕 User not known or password incorrect")
#         else:
#             # Set the login state to True
#             st.session_state["logged_in"] = True
#             return True

#     return False


# # Check if the user is logged in
# if check_password():
#     # Hide the login form and display the main application content
#     st.success(f"You are logged in! {st.session_state['logged_in_user']}")
#     # Logout button to allow the user to log out
#     if st.button("Logout"):
#         st.session_state["logged_in"] = False
#         st.session_state["logged_in_user"] = None
#         streamlit_js_eval(js_expressions="parent.window.location.reload()")
# else:
#     # Stop the execution if not logged in, preventing app content from being shown
#     st.stop()
#%%
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

today = pd.to_datetime(dt.datetime.today())
next_month = today + relativedelta(months=1)
next_month
# data = pd.read_csv('TODO.csv', encoding='latin-1', low_memory=False)
# data['DueDate'] = pd.to_datetime(data['DueDate'])
# data.dtypes
