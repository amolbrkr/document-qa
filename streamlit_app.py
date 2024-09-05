import streamlit as st

pages = [
    st.Page("lab1.py", title="Lab 1"),
    st.Page("lab2.py", title="Lab 2", default=True),
]

pg = st.navigation(pages)
pg.run()
