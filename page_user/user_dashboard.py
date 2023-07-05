import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=False)
def raw_data():
    return pd.read_csv("./data/Scrapped_J&T.csv")

@st.cache_data(show_spinner=False)
def dataJnt ():
    return pd.read_csv("./data/model_df.csv")


@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df

def user_dashboard():
    dataset = raw_data()
    cleanset = dataJnt()

    negative = cleanset[cleanset.polarity == "negative"]
    positive = cleanset[cleanset.polarity == "positive"]

    Persentase_negative = (len(negative) / len(dataset)) * 100
    persentase_bulat_negative = round(Persentase_negative)
    Persentase_positive = (len(positive) / len(dataset)) * 100
    persentase_bulat_positive = round(Persentase_positive)

    data_bersih = len(negative) + len(positive)
    data_bersih_persentase = ((len(dataset) - data_bersih)/ data_bersih) * 100
    data_bersih_persentase_bulat = round(data_bersih_persentase)

    st.header("📊 Home",
              help="Menampilkan informasi tentang dataset")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Panjang Data", f"{len(dataset)}")
    col2.metric("Data Bersih",data_bersih,f"-{data_bersih_persentase_bulat}%")
    col3.metric("Negatif", f"{len(negative)}", f"{persentase_bulat_negative}%" , delta_color="inverse")
    col4.metric("Positif", f"{len(positive)}", f"{persentase_bulat_positive}%")

    st.subheader("Dataset yang digunakan")
    top_menu = st.columns(3)
    with top_menu[0]:
        sort = st.radio("Sort Data", options=["Yes", "No"], horizontal=1, index=1)
    if sort == "Yes":
        with top_menu[1]:
            sort_field = st.selectbox("Sort By", options=dataset.columns)
        with top_menu[2]:
            sort_direction = st.radio(
                "Direction", options=["⬆️", "⬇️"], horizontal=True
            )
        dataset = dataset.sort_values(
            by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
        )
    pagination = st.container()

    bottom_menu = st.columns((4, 1, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox("Page Size", options=[25, 50, 100, 1000])
    with bottom_menu[1]:
        total_pages = (
            int(len(dataset) / batch_size) if int(len(dataset) / batch_size) > 0 else 1
        )
        current_page = st.number_input(
            "Page", min_value=1, max_value=total_pages, step=1
        )
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}** ")

    pages = split_frame(dataset, batch_size)
    pagination.dataframe(data=pages[current_page - 1], use_container_width=True)


if __name__ == "__main__":
    user_dashboard()