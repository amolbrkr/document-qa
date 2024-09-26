import streamlit as st

pages = [
    st.Page("lab1.py", title="Lab 1"),
    st.Page("lab2.py", title="Lab 2"),
    st.Page("lab3.py", title="Lab 3"),
    st.Page("lab4.py", title="Lab 4"),
    st.Page("lab5.py", title="Lab 5", default=True),
]

pg = st.navigation(pages)
pg.run()
