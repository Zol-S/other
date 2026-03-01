import datetime
import streamlit as st

## app
import utils.config_reader
from core.agent import invoke_llm
from utils.histogram_draw import histogram_with_datetime_x

def draw_history():
    if "history" in st.session_state:
        fig = histogram_with_datetime_x(st.session_state.history)

        if "history_chart" not in st.session_state:
            st.session_state.history_chart = st.empty()

        st.session_state.history_chart.plotly_chart(fig)

st.set_page_config(page_title="Market Analysis Tool Demo", page_icon="🤖", layout="centered")

st.title("Agentic Market Analysis Tool Demo")
st.caption("Ask something about a stock or a company and get investment recommendation")

with st.sidebar:
    st.header("History")
    draw_history()

user_question = st.text_area("Your question", height=140, placeholder="e.g., Shall I invest in OpenAI?")

run = st.button("Submit", type="primary", disabled=not user_question.strip())

if run:
    with st.spinner("Thinking..."):
        response, finish_reason = invoke_llm(question=user_question)

        if "history" not in st.session_state:
            st.session_state.history = []

        st.session_state.history.append({
            'datetime': datetime.datetime.now(),
            'success': finish_reason == 'stop'
        })
    
    st.subheader("Recommendation")
    st.code(response, language="text")
    
    with st.sidebar:
        draw_history()