import streamlit as st

st.set_page_config(layout="wide")

col1, col2, col3 = st.columns([3,1,3])
with col2:
    st.image("logo.png", width = 200)

with st.container():
    st.markdown(
        """
        <style>
        .green-bar {
            background-color: #B7D292;
            width: 100%;
            text-align: center;
            font-size: 22px;
            color: #b4C3D03
        }
        </style>
        <div class="green-bar"> Your guide to stylish and sustainable choices </div>
        """,
        unsafe_allow_html=True
    )


userInput = st.chat_input("Ask me anything...")
