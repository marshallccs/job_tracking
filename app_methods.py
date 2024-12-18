import datetime as dt
from dateutil.relativedelta import relativedelta
import time

import numpy as np
import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.metric_cards import style_metric_cards


@st.cache_resource
def get_gspread_client():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets['google'], scope
    )
    client = gspread.authorize(creds)
    return client

@st.cache_data
def fetch_sheet_data(_sheet):
    worksheet = _sheet.get_all_records()
    df = pd.DataFrame(worksheet)
    return df


client = get_gspread_client()
sheet = client.open('extracts_todo').sheet1

class Production:
    def __init__(self):
        # self.df = pd.read_csv("TODO.csv", encoding="latin-1", low_memory=False)
        self.dealerlist = pd.read_csv('DealerList.csv', encoding='latin-1', low_memory=False)
        self.jobs_df = pd.DataFrame()
        self.today = pd.to_datetime(dt.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))
        self.display_date = pd.to_datetime(dt.datetime.today().strftime("%Y/%m/%d"))
        self.new_status = ""

    def format_data(self):
        df = fetch_sheet_data(sheet)
        # st.dataframe(self.jobs_df.dtypes)
        if df['DueDate'].dtype == object:
            df['DueDate'] = pd.to_datetime(df['DueDate'])
        df['AddedDate'] = pd.to_datetime(df['AddedDate'])
        df['ExtractID'] = df['ExtractID'].fillna(0)
        self.jobs_df = df.copy()

    def display_data(self, user_type, full_name):
        self.format_data()
        if st.button("Refresh Table"):
            st.rerun()

        self.user_displays(user_type, full_name)

    def user_displays(self, user_type, full_name):
        self.format_data()

        # Adhoc dataset
        adhoc_df = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Adhoc') & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna())), ['id', 'GroupName', 'Franchise', 'Dealers', 'Criteria', 'ExtractType', 'ShotID', 'ExtractID', 'DueDate', 'Notes', 'AddedDate', 'status']].copy()

        # Adhoc dataset per AM
        adhoc_am_df = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Adhoc') & (self.jobs_df['AddedBy'] == full_name) & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna())), ['id', 'GroupName', 'Franchise', 'Dealers', 'Criteria', 'ExtractType', 'ShotID', 'ExtractID', 'DueDate', 'Notes', 'AddedDate', 'status']].copy()

        # Adhoc dataset per AM
        adhoc_sending_df = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Adhoc') & (self.jobs_df['AddedBy'] == full_name) & (self.jobs_df['status'] == 'Ready for Sending'), ['id', 'GroupName', 'Franchise', 'Dealers', 'Criteria', 'ExtractType', 'ShotID', 'ExtractID', 'DueDate', 'Notes', 'AddedDate', 'status']].copy()
        
        # Daily dataset
        daily_df = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Daily') & (self.jobs_df['DueDate'] <= (self.display_date)) & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna())), ['id', 'GroupName', 'Franchise', 'Dealers', 'Criteria', 'ExtractType', 'ShotID', 'ExtractID', 'DueDate', 'Notes', 'AddedDate']].copy()

        # Weekly dataset
        weekly_df = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Weekly') & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna())), ['id', 'GroupName', 'Franchise', 'Dealers', 'Criteria', 'ExtractType', 'ShotID', 'ExtractID', 'DueDate', 'Notes', 'AddedDate']].copy()

        # Monthly dataset
        monthly_df = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Monthly') & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna())), ['id', 'GroupName', 'Franchise', 'Dealers', 'Criteria', 'ExtractType', 'ShotID', 'ExtractID', 'DueDate', 'Notes', 'AddedDate']].copy()
        

        task_radio = st.radio('Task Navigation', options=['All Data', 'Add Task'], horizontal=True)
        
        if task_radio == 'All Data':
            if user_type == 1:
                # Data Dep Metrics
                data_col1, data_col2, data_col3, data_col4 = st.columns(4)
                with data_col1:
                    st.metric(label='Adhoc', value=adhoc_df['id'].count(), delta='')
                with data_col2:
                    st.metric(label='Daily', value=daily_df['id'].count(), delta='')
                with data_col3:
                    st.metric(label='Weekly', value=weekly_df['id'].count(), delta='')
                with data_col4:
                    st.metric(label='Monthly', value=monthly_df['id'].count(), delta='')
                
                style_metric_cards(background_color='#ffffff', border_left_color='#18334C', box_shadow=True)

                navigation_pane = st.radio(label='Navigation Pane', options=['Adhoc', 'Daily', 'Weekly', 'Monthly'], horizontal=True)
                if navigation_pane == 'Adhoc':
                    self.update_job(adhoc_df, "Ready for Sending", 1, user_type, 'adhoc_key')
                elif navigation_pane == 'Daily':
                    self.update_job(daily_df, "", 2, user_type, 'daily_key')
                elif navigation_pane == 'Weekly':
                    self.update_job(weekly_df, "", 3, user_type, 'weekly_key')
                elif navigation_pane == 'Monthly':
                    self.update_job(monthly_df, "", 4, user_type, 'monthly_key')
            elif user_type == 2:
                # Account Manager Metrics
                am_col1, am_col2 = st.columns(2)
                with am_col1:
                    st.metric(label='New Extracts', value=adhoc_am_df['id'].count(), delta='')
                with am_col2:
                    st.metric(label='Ready for Sending', value=adhoc_sending_df['id'].count(), delta='')

                style_metric_cards(background_color='#ffffff', border_left_color='#18334C', box_shadow=True)

                am_radio = st.radio('Naviation Pane', options=['New', 'Ready for Sending'], horizontal=True)
                if am_radio == "New":
                    self.update_job(adhoc_am_df, '', 1, user_type, 'adhoc_am_key')
                elif am_radio == "Ready for Sending":
                    self.update_job(adhoc_sending_df, 'Complete', 1, user_type, 'adhoc_send_key')
        elif task_radio == 'Add Task':
            self.add_job(full_name)



    def add_job(self, full_name):
        # Add a new job
        self.format_data()
        st.subheader("Add New Task")
        id_list = self.jobs_df['id'].tolist()
        id_list.sort()
        job_id = id_list[-1] + 1
        group = st.selectbox(label="Group", options=self.dealerlist['gp_Name'].unique().tolist())
        dl_selection = self.dealerlist.query("gp_Name==@group")
        franchise_selection = st.multiselect(label="Franchise", options=dl_selection['fr_FranchiseName'].unique().tolist())
        franchise = ''
        for fr in franchise_selection:
            franchise = franchise + fr + ' | '

        fr_selection = dl_selection.query("gp_Name==@group & fr_FranchiseName==@franchise_selection")
        dealers_selection = st.multiselect(label="Dealers", options=fr_selection['de_DealerName'].unique().tolist())
        dealers = ''
        for dl in dealers_selection:
            dealers = dealers + dl + ' | '

        s_col1, s_col2 = st.columns(2)
        with s_col1:
            shot_id = st.text_input("Shot ID")
        with s_col2:
            extract_type = st.selectbox(label="Extract Type", options=["Customer", "Email", "SMS", "Matchback", "Report"])
        data_criteria = st.text_area("Criteria", height=100)
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            frequency = st.selectbox(label="Frequency", options=["Adhoc", "Daily", "Weekly", "Monthly"])
        with f_col2:
            due_date = st.date_input("Due Date", value=self.today)
            due_date = pd.to_datetime(due_date, format="%Y/%m/%d")
        status = ""
        add_notes = st.text_area("Notes", height=100)

        if st.button("Add Task"):
            new_job = {
                "id": [job_id],
                "GroupName": [group],
                "Franchise": [franchise],
                "Dealers": [dealers],
                "Criteria": [data_criteria],
                "ExtractType": [extract_type],
                "ShotID": [shot_id],
                "AddedDate": [self.today],
                "DueDate": [due_date],
                "Timeline": [frequency],
                "AddedBy": [full_name],
                "status": [status],
                "Notes": [add_notes],
            }
            new_job_df = pd.DataFrame(new_job)
            self.jobs_df = pd.concat([self.jobs_df, new_job_df], ignore_index=True)
            self.jobs_df = self.jobs_df.astype(str)
            sheet.update([self.jobs_df.columns.values.tolist()] + self.jobs_df.values.tolist())

            # self.jobs_df.to_csv("TODO.csv", index=False)
            st.success(f"Job {job_id} added!")
            st.cache_data.clear()
            time.sleep(1)
            st.rerun()

    def update_job(self, display_task, status_update, display_type, user_type, grid_key):
        gb = GridOptionsBuilder.from_dataframe(display_task)
    
        gb.configure_selection('multiple', use_checkbox=True)  # Enable single row selection
        gb.configure_default_column(editable=True)
        gridOptions = gb.build()

        # Display the grid
        grid_response = AgGrid(display_task, gridOptions=gridOptions, enable_enterprise=False, update_mode=GridUpdateMode.MODEL_CHANGED, key=grid_key)

        # Get selected row data
        selected_rows = pd.DataFrame(grid_response.get('selected_rows', []))


        if selected_rows.empty:
            update_button = st.button(label='Update')

            if update_button:
                # Get the aggrid data updates
                aggrid_data = pd.DataFrame(grid_response['data'])
                
                # Compare the aggrid udpated data and update it to the main sheet.
                # Identify common columns for comparison
                common_columns = self.jobs_df.columns.intersection(aggrid_data.columns)

                # Update df1 based on df2
                for _, row in aggrid_data.iterrows():
                    # Locate the row in df1 with the same ID
                    mask = self.jobs_df['id'] == row['id']
                    
                    # If there's a matching row, update it
                    if mask.any():
                        for column in common_columns:
                            self.jobs_df.loc[mask, column] = row[column]
                
                # self.jobs_df.to_csv('TODO.csv', index=False, date_format="%Y/%m/%d")
                self.jobs_df = self.jobs_df.astype(str)
                sheet.update([self.jobs_df.columns.values.tolist()] + self.jobs_df.values.tolist())
                st.success("Task has been updated")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()

        # Ensure selected_rows is not empty
        elif (not selected_rows.empty and user_type == 1) or status_update == 'Complete':  # Check if there's at least one selected row
            task_id = selected_rows['id'].tolist()

            if 'view' not in st.session_state:
                st.session_state.view = 'Close Job'

            def toggle_view():
                if st.session_state.view == 'Close Job':
                    st.session_state.view = 'View Job'
                else:
                    st.session_state.view = 'Close Job'


            # with button_container:
            b_col1, b_col2 = st.columns([0.3,3])
            with b_col1:
                view_task_button = st.button(label='View Job', on_click=toggle_view)
            with b_col2:
                complete_button = st.button(label='Complete')

                if view_task_button and len(task_id) > 1:
                    st.warning("You can only select one job at time to view")
                elif view_task_button and len(task_id) == 1:
                    if st.session_state.view == 'View Job':
                        job_view = display_task.loc[display_task['id'] == task_id[0]].copy()

                        with st.container(border=True):
                            # Display the ID, ShotID and Extract Type
                            id_label_col, shotid_label_col, etype_label_col = st.columns([0.5, 1.5, 1.5])
                            with id_label_col:
                                st.markdown("ID")
                            with shotid_label_col:
                                st.markdown("ShotID")
                            with etype_label_col:
                                st.markdown("Extract Type")

                            id_info_col, shotid_info_col, etype_info_col = st.columns([0.5,1.5,1.5])
                            with id_info_col:
                                id_info_con = st.container(border=True)
                                id_info_con.markdown(job_view['id'].sum())
                            with shotid_info_col:
                                shotid_info_con = st.container(border=True)
                                shotid_info_con.markdown(job_view['ShotID'].fillna(0).astype(int).sum())
                            with etype_info_col:
                                etype_info_con = st.container(border=True)
                                etype_info_con.markdown(job_view['ExtractType'].sum())

                            # Display the dealer info
                            # Dealer Labels
                            gp_label_col, fr_label_col = st.columns([0.5, 3])
                            with gp_label_col:
                                st.markdown("Group Name")
                            with fr_label_col:
                                st.markdown("Franchise")
                            
                            gp_info_col, fr_info_col = st.columns([0.5,3])
                            with gp_info_col:
                                gp_info_con = st.container(border=True)
                                gp_info_con.markdown(job_view['GroupName'].sum())
                            with fr_info_col:
                                fr_info_con = st.container(border=True)
                                fr_info_con.markdown(job_view['Franchise'].sum())

                            st.markdown("Dealers")
                            dl_info_con = st.container(border=True)
                            dl_info_con.markdown(job_view['Dealers'].sum())

                            # Display the criteria
                            st.markdown("Criteria")
                            cr_con = st.container(border=True)
                            cr_con.markdown(job_view['Criteria'].sum())

                            # Display the notes
                            st.markdown("Notes")
                            nt_con = st.container(border=True, height=200)
                            nt_con.markdown(job_view['Notes'].sum())

                    elif st.session_state.view == 'Close Job':
                        pass


                if complete_button:
                    for item in task_id:
                        if display_type == 1:
                            self.jobs_df['status'] = np.where(self.jobs_df['id'] == item, status_update, self.jobs_df['status'])

                            # TODO: Update the completed time after the file status

                            # self.jobs_df.loc[
                            #     self.jobs_df["id"] == item, "JobCompletedTime"
                            # ] = {self.today}
                        elif display_type == 2:
                            self.jobs_df['DueDate'] = np.where(self.jobs_df['id'] == item, self.display_date + dt.timedelta(days=1),  self.jobs_df['DueDate'])
                            self.jobs_df['DueDate'] = pd.to_datetime(self.jobs_df['DueDate']).dt.strftime("%Y/%m/%d")
                        elif display_type == 3:
                            self.jobs_df['DueDate'] = np.where(self.jobs_df['id'] == item, pd.to_datetime(self.jobs_df['DueDate'], format='%Y/%m/%d') + dt.timedelta(days=7), self.jobs_df['DueDate'])
                            # self.jobs_df['DueDate'] = pd.to_datetime(self.jobs_df['DueDate']).dt.strftime("%Y/%m/%d")
                        elif display_type == 4:
                            self.jobs_df['DueDate'] = self.jobs_df.apply(lambda row: row['DueDate'] + relativedelta(months=1) if row['id'] == item else row['DueDate'],axis=1)

                    # self.jobs_df.to_csv('TODO.csv', index=False, date_format="%Y/%m/%d")
                    self.jobs_df = self.jobs_df.astype(str)
                    sheet.update([self.jobs_df.columns.values.tolist()] + self.jobs_df.values.tolist())
                    st.success("Task has been updated")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()




    def overdue_jobs(self):
        # Check overdue jobs
        st.subheader("Overdue Jobs")
        overdue_jobs = self.jobs_df[
            (self.jobs_df["Deadline"] < self.today)
            & (self.jobs_df["Status"] != "Completed")
        ]

        if not overdue_jobs.empty:
            st.warning(f"There are {len(overdue_jobs)} overdue jobs:")
            st.dataframe(overdue_jobs)
        else:
            st.success("No overdue jobs.")
