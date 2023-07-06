import streamlit as st
import function.functions as ft
import pandas as pd

# @st.cache_data
# def data_raw_jnt ():
#     return pd.read_csv("./data/Scrapped_J&T.csv")

@st.cache_data
def dataJnt ():
    return pd.read_csv("./data/model_df.csv")

def admin_upload():
    df = dataJnt()

    # Mengubah kolom 'at' menjadi tipe datetime jika belum
    df['at'] = pd.to_datetime(df['at'])

    # Membuat kolom baru 'year' untuk menyimpan tahun dari kolom 'at'
    df['year'] = df['at'].dt.year

    # Menghitung jumlah nilai positif dan negatif untuk setiap tahun
    df_grouped = df.groupby(['year', 'polarity']).size().unstack(fill_value=0)

    # Menghilangkan tanda koma pada label sumbu x
    df_grouped.index = df_grouped.index

    # Menampilkan line chart menggunakan st.line_chart
    st.line_chart(df_grouped)


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