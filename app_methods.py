import datetime as dt
from dateutil.relativedelta import relativedelta
import time

import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder


class Production:
    def __init__(self):
        self.df = pd.read_csv("TODO.csv", encoding="latin-1", low_memory=False)
        self.dealerlist = pd.read_csv('DealerList.csv', encoding='latin-1', low_memory=False)
        self.jobs_df = pd.DataFrame()
        self.today = pd.to_datetime(dt.datetime.today().strftime("%Y/%m/%d %H:%M:%S"))
        self.display_date = pd.to_datetime(dt.datetime.today().strftime("%Y/%m/%d"))
        self.new_status = ""

    def format_data(self):
        self.jobs_df = self.df.copy()
        # st.dataframe(self.jobs_df.dtypes)
        if self.jobs_df['DueDate'].dtype == object:
            self.jobs_df['DueDate'] = pd.to_datetime(self.jobs_df['DueDate'])
        self.jobs_df['AddedDate'] = pd.to_datetime(self.jobs_df['AddedDate'])

    def display_data(self, displaytype, user_type):
        self.format_data()
        if st.button("Refresh Table"):
            st.rerun()

        self.user_displays(displaytype, user_type)

    def user_displays(self, display_type, user_type):
        self.format_data()
        
        if user_type == 1:
            if display_type == 1:
                # TODO: Check the the date check is not taking into account the time
                display_data = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Adhoc') & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna()))].copy()
                self.update_job(display_data, "Data Complete", 1)
            elif display_type == 2:
                display_data = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Daily') & (self.jobs_df['DueDate'] <= (self.display_date)) & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna()))].copy()
                self.update_job(display_data, "", 2)
            elif display_type == 3:
                display_data = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Weekly') & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna()))].copy()
                self.update_job(display_data, "Data Complete", 3)
            elif display_type == 4:
                display_data = self.jobs_df.loc[(self.jobs_df['Timeline'] == 'Monthly') & ((self.jobs_df['status'] == '') | (self.jobs_df['status'].isna()))].copy()
                self.update_job(display_data, "Data Complete", 4)


    def add_job(self):
        # Add a new job
        # TODO: Do a check to see if the jobID is available on update. If its already in the list, create a new one.
        self.format_data()
        st.subheader("Add New Task")
        id_list = self.jobs_df['id'].tolist()
        id_list.sort()
        new_jobid = str(id_list[-1] + 1)
        job_id = st.text_input("Job ID", value=new_jobid)
        group = st.selectbox(label="Group", options=self.dealerlist['gp_Name'].unique().tolist())
        dl_selection = self.dealerlist.query("gp_Name==@group")
        franchise = st.multiselect(label="Franchise", options=dl_selection['fr_FranchiseName'].unique().tolist())
        fr_selection = dl_selection.query("gp_Name==@group & fr_FranchiseName==@franchise")
        dealers = st.multiselect(label="Dealers", options=fr_selection['de_DealerName'].unique().tolist())
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
                "status": [status],
                "Notes": [add_notes],
            }
            new_job_df = pd.DataFrame(new_job)
            self.jobs_df = pd.concat([self.jobs_df, new_job_df], ignore_index=True)
            self.jobs_df.to_csv("TODO.csv", index=False)
            st.success(f"Job {job_id} added!")
            time.sleep(1)
            st.rerun()

    def update_job(self, display_task, status_update, display_type):
        gb = GridOptionsBuilder.from_dataframe(display_task)
    
        gb.configure_selection('multiple', use_checkbox=True)  # Enable single row selection
        # gb.configure_default_column(editable=True)
        gridOptions = gb.build()

        # Display the grid
        grid_response = AgGrid(display_task, gridOptions=gridOptions, enable_enterprise=False)

        # Get selected row data
        selected_rows = pd.DataFrame(grid_response.get('selected_rows', []))

        # Ensure selected_rows is not empty
        if not selected_rows.empty:  # Check if there's at least one selected row
            task_id = selected_rows['id'].tolist()


        # Create a form to edit the status
            with st.form(key='edit_status_form'):
                submit_button = st.form_submit_button(label='Complete')

                if submit_button:
                    # Update the task's status
                    for item in task_id:
                        if display_type == 1:
                            self.jobs_df['status'] = np.where(self.jobs_df['id'] == item, status_update, self.jobs_df['status'])
                            # self.jobs_df.loc[
                            #     self.jobs_df["id"] == item, "JobCompletedTime"
                            # ] = {self.today}
                        elif display_type == 2:
                            self.jobs_df['DueDate'] = np.where(self.jobs_df['id'] == item, self.display_date + dt.timedelta(days=1),  self.jobs_df['DueDate'])
                            self.jobs_df['DueDate'] = pd.to_datetime(self.jobs_df['DueDate']).dt.strftime("%Y/%m/%d")
                        elif display_type == 3:
                            self.jobs_df['DueDate'] = np.where(self.jobs_df['id'] == item, pd.to_datetime(self.jobs_df['DueDate'], format="%Y/%m/%d") + dt.timedelta(days=7), self.jobs_df['DueDate'])
                            self.jobs_df['DueDate'] = pd.to_datetime(self.jobs_df['DueDate']).dt.strftime("%Y/%m/%d")
                        elif display_type == 4:
                            # TODO: Check the month data error and resolve.
                            self.jobs_df['DueDate'] = self.jobs_df.apply(lambda row: row['DueDate'] + relativedelta(months=1) if row['id'] == item else row['DueDate'],axis=1)
                    self.jobs_df.to_csv('TODO.csv', index=False, date_format="%Y/%m/%d")
                    st.success("Task has been updated")
                    time.sleep(1)
                    st.rerun()

                # TODO: Create a view button that displays the job of the selected

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
