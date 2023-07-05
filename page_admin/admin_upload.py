import streamlit as st
import function.functions as ft
import pandas as pd

@st.cache_data
def data_raw_jnt ():
    return pd.read_csv("./data/Scrapped_J&T.csv")

def admin_upload():
    data_raw = data_raw_jnt()
    df, hasil_positive, hasil_negative = ft.hasilFileMining(data_raw,'content')
    st.write({
        "hasil positif" : hasil_positive,
        "hasil negative" : hasil_negative
    })
    kamus = ft.hitung_kamus(df)
    st.write(kamus)

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