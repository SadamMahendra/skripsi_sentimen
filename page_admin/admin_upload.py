import streamlit as st
import function.functions as ft
import pandas as pd
from deta import Deta

deta = Deta(st.secrets["db_key"])
db = deta.Base("newData")

def insert_user(nim,name,jurusan):
    try:
        db.put({"key": nim, "name": name, "jurusan": jurusan})
        return st.success("Berhasil")
    except:
        return st.warning("gagal") 


def admin_upload():

    nim = st.text_input("nim")
    nama = st.text_input("nama")
    jurusan = st.selectbox("jurusan",['IT','SI'])

    submit = st.button("submit")
    if submit:
        insert_user(nim,nama,jurusan)
        
    # col1, col2, col3 = st.columns(3)
    # col1.metric("Temperature", "70 °F")
    # col2.metric("Wind", "9 mph", "-8%")
    # col3.metric("Humidity", "86%", "4%")


    # data = db.db_drive.get("model_df.csv")
    # df = pd.read_csv(data)

    # st.write(df)

    # file = st.file_uploader("masukan file", type="csv")
    # submit = st.button("lohe")

    # if submit:
    #     db.db_drive.put(file.name, data=file)

if __name__ == "__main__":
    admin_upload()