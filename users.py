import hmac
import streamlit as st

def check_password():
    """Returns `True` if the user has entered a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            st.session_state["logged_in"] = True  # Set logged_in state
            st.session_state["logged_in_user"] = st.session_state["username"]
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    # Check if the user is already logged in
    if st.session_state.get("logged_in", False):
        return True

    # If not logged in, display the login form
    login_form()

    if "password_correct" in st.session_state:
        if not st.session_state["password_correct"]:
            st.error("😕 User not known or password incorrect")
        else:
            # Set the login state to True
            st.session_state["logged_in"] = True
            return True

    return False

