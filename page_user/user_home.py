import streamlit as st
from function.functions import hasilUltimatum

def homePage():
    st.header("Streamlit Predictor")
    rawText =  st.text_area("Masukan Text disini :")
    submitButton = st.button("analisis")
    if submitButton:
        score,polarity,result = hasilUltimatum(rawText)
        col1,col2 = st.columns(2)
        if polarity == 'negative':
            with col1:
                st.warning(f"Polarity berdominan {polarity} dengan score {score}")
            with col2:
                st.write(result)
        elif polarity == 'positive':
            with col1:
                st.success(f"Polarity berdominan {polarity}")
            with col2:
                st.write(result)
        else:
            with col1:
                st.info(f"Polarity berdominan {polarity}")
            with col2:
                st.write(result)

if __name__ == "__main__":
    homePage()