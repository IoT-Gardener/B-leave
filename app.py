import asyncio
import logging
import os
import requests
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path
from PIL import Image
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from streamlit_lottie import st_lottie
from wordcloud import WordCloud, ImageColorGenerator

# Set the page title and icon and set layout to "wide" to minimise margains
st.set_page_config(page_title="B-Leave", page_icon=":dragon:")

def load_assets(url: str) -> dict:
    """Function load asset from a http get request

    Args:
        url (str): URL of the asset to load

    Returns:
        dict: _description_
    """
    asset = requests.get(url)
    if asset.status_code != 200:
        logging.error("Failed to load asset")
        return None
        
    else:
        logging.info("Asset loaded successfully")
        return asset.json()

async def countdown(container: st.delta_generator.DeltaGenerator):
    # Function to do a running countdown until a given date, and output results to a container

    # :param container: The container to output the time to
    # :type container: st.delta_generator.DeltaGenerator

    # Run infinitely
    while True:
        # Calculate the timedelta between a given date, and now.
        time_diff = datetime.strptime("08/01/23 11:00:00", '%m/%d/%y %H:%M:%S') - datetime.now()
        # Find the total number of seconds until the given date
        total_seconds = int(time_diff.seconds)
        # Calculate how many hours there are, and how many seconds are left
        hours, remainder = divmod(total_seconds, 3600)
        # Calculate the number of minutes, and the remaining seconds
        minutes, seconds = divmod(remainder,60)

        # Create markdown for the container
        container.markdown(
            f"""
            <p class="time">
                {time_diff.days}:{hours}:{minutes}:{seconds}
            </p>
            """, unsafe_allow_html=True)
        # Wait for one second to update
        r = await asyncio.sleep(1)

# Add styling to the countdown
st.markdown(
    """
    <style>
    .time {
        font-size: 60px !important;
        font-weight: 500 !important;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

mongo_user = st.secrets["MONGO_USER"]
mongo_pass = st.secrets["MONGO_PASS"]
uri = f"mongodb+srv://{mongo_user}:{mongo_pass}@attendeedb.wbslhme.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["Winter23"]
col = db["Winter23Attendees"]

# Load assets
lottie_fire = load_assets("https://assets8.lottiefiles.com/packages/lf20_uu7qI3.json")

img_path = Path(__file__).parents[0]
logo_img = Image.open(f"{img_path}/Images/Logo.png")
mask_img = Image.open(f"{img_path}/Images/A_Symbol.jpg")

# Header section
with st.container():
    # Create columns
    head_l, head_r = st.columns((2,1))
    
    with head_l:
        # Add a subheader
        st.subheader("Become a B-leaver")
        # Add a title
        st.title("B-Leave Summit 2023")
    
    with head_r:
        # Add logo
        st.image(logo_img)
    
    # Add some description
    st.write("Within the confines of a struggling potato agri-tech company, a remarkable journey unfolded. As a group of employees faced challenges and uncertainties, their bonds grew stronger, providing solace and unwavering support in the midst of adversity. One by one, they discovered their true potential and found the courage to break free from their shackles, embarking on new paths. Despite parting ways, their friendship endured, eternal flames that illuminated their lives, reminding them of the strength forged in the crucible of their shared struggles.")
    # Add a lottie animation
    st_lottie(lottie_fire)
    # Add a line divider
    st.write("---")


# Countdown section
with st.container():
    # Add a title
    st.header("What is this?")
    # Add some text
    st.write("A very valid question. B-Leave Summit 2023 is a gathering for B-Leavers, B-Wives, and others who are yet still lost. We will drink, we will feast, we will complain, as we adventure to a land far far away from the troubles of gimbles and yield.")
    #At some more text
    st.write("This will be a week long adventure to the wild lands of the UK (final location pending selection of a optimal date) where we will gathering a giant house/cabin/barn in the middle of nowhere and have a big ol' Holiday. There will be a fire, and the will most likely be a hot tub.")
    # Add even more text
    st.write("The countdown is on until the events of B-Leave Summit 2023 are finalised. Confirm your attendence, and vote for a date that suits you!")

    # Create a container to store the timer
    countdown_container = st.empty()

    survery_l, survey_r = st.columns((1,1))
    with survery_l: 
        # Add text input to enter name
        name = st.text_input('Please enter your name.')
        # Add checkbox to select if you are attending
        attending = st.checkbox('I would like to attend B-Leave Summit 2023')
        # Add radio button to answer the silly question
        fight = st.radio("I would rather fight:", ('42 duck size horses', '1 horse size duck'))

    with survey_r:
        # Add multi choice to select dates
        dates = st.multiselect('Which date(s) work for you?', ['Week of 09/10', 'Week of 16/10'])
        # Add radio button to select what you are
        role = st.radio("I am:", ('a B-Leaver', 'a B-Wife', 'still suffering', 'other'))

    # Add a button
    if st.button('Submit'):
        # Assign week boolean based on multiselect responses
        week_09 = True if 'Week of 09/10' in dates else False
        week_16 = True if 'Week of 16/10' in dates else False
        # Create dictionary of responses
        submission = {
            "Name": name,
            "Attending": attending,
            "09/10": week_09,
            "16/10": week_16,
            "Fight": fight,
            "Role": role
        }
        # Attempt to upload response to DB
        try:
            col.insert_one(submission)
            st.write("Submission successful!")
        except:
            st.write("Submission failed!")
    # Add a line divider
    st.write("---")


# Insight section
with st.container():
    # Add a title
    st.header("B-Leaver Insights")
    # Add some text
    st.write("What would life be without some data?!")

    # Read all the data from the database.
    data = col.find()
    # Convert data to a pandas dataframe
    df = pd.DataFrame(list(data))

    # Get a list of the unique roles
    roles = df['Role'].unique()
    # Create list to store count for each role
    role_counts = []
    # Populate the list with the number of roles
    for role in roles:
        role_counts.append(df.Role.value_counts()[role])
    # Create a list of dictionaries with the number of horse/duck fighters for each date
    date_dicts = [
        {
            "Date": "09/10",
            "type": "Duck fighter",
            "Votes": len(df.loc[(df['09/10'] == True) & (df['Fight'] == "1 horse size duck") & (df['Attending'] == True)])
        },
        {
            "Date": "09/10",
            "type": "Horse fighter",
            "Votes": len(df.loc[(df['09/10'] == True) & (df['Fight'] == "42 duck size horses") & (df['Attending'] == True)])
        },
        {
            "Date": "16/10",
            "type": "Duck fighter",
            "Votes": len(df.loc[(df['16/10'] == True) & (df['Fight'] == "1 horse size duck") & (df['Attending'] == True)])
        },
        {
            "Date": "16/10",
            "type":  "Horse fighter",
            "Votes": len(df.loc[(df['16/10'] == True) & (df['Fight'] == "42 duck size horses") & (df['Attending'] == True)])
        }
    ]
    # Get only the names of people attending
    names_going = df.loc[df['Attending'] == True, 'Name']
    # Get the number of horse fighters
    no_horse_fighters = len(df.loc[df['Fight'] == "1 horse size duck"])
    # Get the number of duck fighters
    no_duck_fighters = len(df.loc[df['Fight'] == "42 duck size horses"])

    # Create 3 columns for metrics
    metrics_l, metrics_m, metrics_r = st.columns((1,1,1))
    with metrics_l:
    # Display a metric with the number of attendees
        st.metric(
            label="Summit Attendees",
            value=f"{len(names_going)}/{len(df)}",
            help="The total number of people who have said they are attending."
        )
    with metrics_m:
        # Add metric with number of horse fighters
        st.metric(
            label="Horse fighters",
            value=no_horse_fighters,
            delta=no_horse_fighters-no_duck_fighters,
            help="The number of people who would rather fight 42 duck size horses"
        )
    with metrics_r:
        # Add metric with number of duck fighters
        st.metric(
            label="Duck fighters",
            value=no_duck_fighters,
            delta=no_duck_fighters-no_horse_fighters,
            help="The number of people who would rather fight 1 horse size duck"
        )

    # Create two columns for insights
    insights_l, insights_r = st.columns((1,1))

    # Populate the left column
    with insights_l:
        st.write("Who is going?")
        # Create word cloud use given shape and colouring
        wordcloud = WordCloud(repeat=True, mask=np.array(mask_img)).generate(" ".join(names_going   ))
        wordcloud.recolor(color_func=ImageColorGenerator(np.array(mask_img)))
        # Display the generated word cloud
        st.image(wordcloud.to_array(), use_column_width=True)

    # Populate the right column
    with insights_r:
        st.write("Who makes up the B-Leavers")
        source = pd.DataFrame({"category": roles, "values": role_counts})
        # Create pie chart
        base = alt.Chart(source).encode(
            theta=alt.Theta("values:Q", stack=True),
            radius=alt.Radius("values", scale=alt.Scale(type="sqrt", zero=True, rangeMin=20)),
            color=alt.Color("category:N", scale=alt.Scale(scheme="darkred"))
        )
        # Add in inner cirlce
        c1 = base.mark_arc(innerRadius=20, stroke="#fff")
        # Display the chart
        st.altair_chart(c1, use_container_width=True)

    st.write("What is the best date?")
    source = pd.DataFrame(date_dicts)
    # Create a bar chart
    base2 = alt.Chart(source).mark_bar().encode(
        x='Votes',
        y='Date',
        color=alt.Color('type', scale=alt.Scale(scheme="darkred"))
    )
    # Display the chart
    st.altair_chart(base2, use_container_width=True)

    st.write("---")


# Footer section
with st.container():
    st.write("""
    **Author**: Alex.B, :wave: [LinkedIn](https://www.linkedin.com/in/alexander-billington-29488b118/) 
    :books: [Github](https://github.com/IoT-Gardener) :computer: [Website](https://abmlops.streamlit.app)
    """)

asyncio.run(countdown(countdown_container))