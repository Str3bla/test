import streamlit as st
import pandas as pd
import numpy as np

job_step = st.sidebar.select_slider(
    "Select a step in the applicant process to ANALYZE",
    options=[
        "Apply",
        "Reviewed",
        "Screen",
        "Interview",
        "Offer",
        "Ready for Hire",
    ],
)

st.sidebar.write("")

option = st.sidebar.selectbox(
    'What do you want to compare it to?',
    ('Rejected/Declined','Apply','Reviewed','Screen','Interview','Offer','Ready for Hire'))

st.sidebar.write("")

option1 = st.sidebar.multiselect(
    'What Business Units?',
    ['Finance','Marketing','HR','Operations','Product','Sales'])

st.sidebar.write("")

st.sidebar.write('What challenges do you want TA GPT to help with?')

Scenario_TTF = st.sidebar.checkbox("Time to Fill")
Scenario_Difficulty = st.sidebar.checkbox("Location")
Scenario_Conversion = st.sidebar.checkbox("Conversion")
Scenario_Quantity = st.sidebar.checkbox("Compensation")

st.write("Segmented Trending by ", job_step)
chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)

st.write("")
st.write("")
st.write("")

# st.latex(r'''
#     a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
#     \sum_{k=0}^{n-1} ar^k =
#     a \left(\frac{1-r^{n}}{1-r}\right)
#     ''')

st.write("")
st.write("")
st.write("")

st.title('Customizing the theme of Streamlit apps')

st.write('Contents of the `.streamlit/config.toml` file of this app')

st.code("""
[theme]
primaryColor="#F39C12"
backgroundColor="#2E86C1"
secondaryBackgroundColor="#AED6F1"
textColor="#FFFFFF"
font="monospace"
""")

st.write("")
st.write("")
st.write("")

st.title('st.progress')

with st.expander('About this app'):
     st.write('You can now display the progress of your calculations in a Streamlit app with the `st.progress` command.')

my_bar = st.progress(0)

for percent_complete in range(100):
     time.sleep(0.05)
     my_bar.progress(percent_complete + 1)

st.balloons()
