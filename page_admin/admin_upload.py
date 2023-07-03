import streamlit as st
import function.config as db
import pandas as pd

def admin_upload():
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", "70 °F")
    col2.metric("Wind", "9 mph", "-8%")
    col3.metric("Humidity", "86%", "4%")


    # data = db.db_drive.get("model_df.csv")
    # df = pd.read_csv(data)

    # st.write(df)

    # file = st.file_uploader("masukan file", type="csv")
    # submit = st.button("lohe")

    # if submit:
    #     db.db_drive.put(file.name, data=file)

if __name__ == "__main__":
    admin_upload()