import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime

def extract_date(filename):
    if " till " in filename:
        date_str = filename.split(" till ")[0].replace(" ", "")
    elif '_' in filename:
        date_str = filename.split("_")[1].split(".")[0]
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        date_str = filename.split(".")[0].replace(" ", "")
    return datetime.datetime.strptime(date_str, "%Y-%m").date()

rental_dir = os.getcwd() + '\\rental_csv'


# Adjust the width of the main content area
st.markdown(
    """
    <style>
    .reportview-container .main .block-container{
        max-width: 12000px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
@st.cache_data(ttl=10800)
def get_data():

    files = os.listdir('rental_csv')
    dates = [extract_date(filename) for filename in files]

    col_names = ['Ejari Contract Number','Registration Date','Start Date','End Date','Property ID','Version','Area','Contract Amount','Annual Amount','Is Free Hold?','Property Size (sq.m)','Property Type','Property Sub Type','Number of Rooms','Usage','Nearest Metro','Nearest Mall',	'Nearest Landmark',	'Parking','No of Units','Master Project','Project']

    dtypes = {'Ejari Contract Number':str,'Property ID':str,'Version':str,'Area':str,'Contract Amount':float,'Annual Amount':float,'Is Free Hold?':str,'Property Size (sq.m)':float,'Property Type':str,'Property Sub Type':str,'Number of Rooms':str,'Usage':str,'Nearest Metro':str,'Nearest Mall':str,'Nearest Landmark':str,'Parking':str,'No of Units':str,'Master Project':str,'Project':str}

    values = {'Ejari Contract Number':0,'Registration Date':0,'Start Date':0,'End Date':0,'Property ID':'0','Version':'None','Area':'None','Contract Amount':0,'Annual Amount':0,'Is Free Hold?':'None','Property Size (sq.m)':0,'Property Size (sq.ft)':0,'Amount (sq.m)':0,'Amount (sq.ft)':0,'Property Type':'None','Property Sub Type':'None','Number of Rooms':'None','Usage':'None','Parking':'None','No of Units':'None','Master Project':'None','Project':'None'}

    empty_list = []

    for filename in os.listdir('rental_csv'):
        if filename.endswith('.csv'):
            print(filename)
            df = pd.read_csv(os.path.join('rental_csv/', filename), dtype=dtypes)
            df.fillna(0)
            df = df.drop(columns=["Nearest Metro","Parking","Nearest Mall", "Nearest Landmark"])
            empty_list.append(df)

    raw_data = pd.concat(empty_list)

    count_row = raw_data.shape[0]

    size_list = [0]*count_row

    raw_data.insert(11,"Property Size (sq.ft)",size_list,True)
    raw_data.insert(12,"Amount (sq.m)",size_list,True)
    raw_data.insert(13,"Amount (sq.ft)",size_list,True)

    raw_data["Property Size (sq.ft)"] = raw_data["Property Size (sq.m)"] * 10.7639104167
    raw_data["Amount (sq.m)"] = raw_data["Contract Amount"] / raw_data["Property Size (sq.m)"]
    raw_data["Amount (sq.ft)"] = raw_data["Contract Amount"] / raw_data["Property Size (sq.ft)"]

    raw_data['Project'] = raw_data['Project'].str.title()
    raw_data['Area'] = raw_data['Area'].str.title()

    raw_data['Registration Date'] = pd.to_datetime(raw_data['Registration Date']).dt.date
    raw_data['Start Date'] = pd.to_datetime(raw_data['Start Date']).dt.date
    raw_data['End Date'] = pd.to_datetime(raw_data['End Date']).dt.date

    raw_data.sort_values(by='Registration Date', inplace = True)

    raw_data.fillna(value = values, inplace = True)

    raw_data = raw_data.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
    return raw_data


df = get_data().reset_index(drop=True)

'# Rental Data'
# Forms can be declared using the 'with' syntax

# Getting the Unique Projects,Areas from the data and adding them onto a single variable
projects_areas = ['All'] + sorted(df['Project'].unique().tolist()) + sorted(df['Area'].unique().tolist())
projects = df['Project'].unique()
areas = df['Area'].unique()
# Getting the Unique Rooms from the data
rooms = ['All'] + df['Number of Rooms'].unique().tolist()
# Getting the Unique Property Sub type from the data
property_sub_type_list = ['All'] + df['Property Sub Type'].unique().tolist()
# setting the property type into a list
property_type_list = ['All','Land','Unit','Building']
# setting the version into a list
version_list = ['All','New','Renewal']
# setting the usage type into a list
usage_type_list = ['All','Residential','Commercial','Other']
# setting the default date to 01 january 2022
start_date_default = datetime.datetime(2022, 1, 1).date()

with st.form(key='my_form', clear_on_submit = True):
    project_area = st.selectbox('Search Project or Area', projects_areas, key='project+area')
    with st.expander("Filter"):
        c1, c2, c3, c4 = st.columns(4)
        b1, b2, b3 = st.columns(3)
        with c1:
            start_date = st.date_input('Start Date', key='start_date',value = start_date_default, max_value=datetime.datetime.today())
        with c2:
            property_type = st.selectbox('Property Type', property_type_list, key='property_type')
        with c3:
            room = st.selectbox('Number of Rooms', rooms, key='room')
        with c4:
            usage_type = st.selectbox('Usage',usage_type_list, key='usage_type')
        with b1:
            version = st.selectbox('Version', version_list, key='Version')
        with b2:
            property_sub_type = st.selectbox('Property Sub Type', property_sub_type_list, key='property_sub_type')
    
    submit_button = st.form_submit_button(label='Submit')


    if submit_button:

        mask = pd.Series(np.ones(df.shape[0], dtype=bool))

        if project_area != 'All':
            if project_area in projects:
                mask &= df['Project'] == project_area
            elif project_area in areas:
                mask &= df['Area'] == project_area

        if property_type != 'All':
            mask &= df['Property Type'] == property_type

        if room != 'All':
            mask &= df['Number of Rooms'] == room

        if usage_type != 'All':
            mask &= df['Usage'] == usage_type

        if version != 'All':
            mask &= df['Version'] == version

        if property_sub_type != 'All':
            mask &= df['Property Sub Type'] == property_sub_type


        if start_date:
            #start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
            mask &= df['Start Date'] >= start_date


        matching_rows = df[mask].reset_index(drop=True)
        if matching_rows.empty:
            st.warning("No matching data found.")
        else:
            st.dataframe(matching_rows,width=2000, height=None)
