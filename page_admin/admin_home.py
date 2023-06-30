import streamlit as st
import pandas as pd
import function.functions as ft
from sklearn.model_selection import train_test_split
from sklearn import metrics
import pickle
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import classification_report

#import model
pickle_in = open('./data/model.pkl', 'rb')
svm,tfidf = pickle.load(pickle_in)


def prediction(X_train, X_test, y_train, y_test):
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    score = metrics.accuracy_score(y_test, y_pred)
    return score

@st.cache_data
def data_raw_jnt ():
    return pd.read_csv("./data/Scrapped_J&T.csv")

def admin_home():
    selected = option_menu(
        None, ["Data Visualisasi","Sentimen Predictor File"], 
        icons=['bar-chart-fill',"file-earmark-plus"], 
        menu_icon="cast", 
        default_index=0, 
        orientation="horizontal"
        )
    
    if selected == "Data Visualisasi":
        data_raw = data_raw_jnt()

        st.header("Proses Data")
        st.write("Memperlihatkan Pre Processing yang ada di dalam dataset JnT")
        
        st.subheader("Raw Data")
        st.write("Berisikan data yang belum di olah")
        st.write(data_raw)

        #@st.cache_data(show_spinner="Data Cache untuk proses sedang disiapkan")
        def load_proses():
            df, hasil_positive, hasil_negative = ft.hasilFileMining(data_raw,'content')
            top_10_positive, top_10_negative = ft.process_top_10_words(hasil_positive, hasil_negative)
            ranking = ft.calculate_tfidf_ranking(df)
            X, y = ft.process_data(df)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
            predic, svm, y_pred = ft.predic_SVM(X_train, X_test, y_train, y_test)

            # Simpan laporan klasifikasi dalam variabel
            report = classification_report(y_test, y_pred, output_dict=True)

            # Konversi laporan menjadi DataFrame pandas
            df_classification_report = pd.DataFrame(report).transpose()
            
            accuracy = f"{predic.round(2)*100}%"
            
            #menampilkan grafik line tentang polarity pertahun
            df['at'] = pd.to_datetime(df['at'])
            df['tahun'] = df['at'].dt.year
    
            # Menghitung jumlah kalimat negatif dan positif per tahun sampai tahun terakhir dalam dataframe
            tahun_terakhir = df['tahun'].max()
            df_filtered = df[df['tahun'] <= tahun_terakhir]
            jumlah_negatif = df_filtered[df_filtered['polarity'] == 'negative'].groupby('tahun').size().reindex(range(df_filtered['tahun'].min(), tahun_terakhir+1), fill_value=0)
            jumlah_positif = df_filtered[df_filtered['polarity'] == 'positive'].groupby('tahun').size().reindex(range(df_filtered['tahun'].min(), tahun_terakhir+1), fill_value=0)

            # Membuat grafik menggunakan st.line_chart()
            data_chart = pd.DataFrame({
                'negative': jumlah_negatif,
                'positive': jumlah_positif
            })

            return df, accuracy, top_10_positive, top_10_negative, ranking, data_chart, X_test, y_test, y_train, y, svm, df_classification_report

        df, accuracy, top_10_positive, top_10_negative, ranking, data_chart, X_test, y_test, y_train, y, svm, df_classification_report = load_proses()

        #@st.cache_data(show_spinner="Data chace untuk show data sedang disiapkan")
        def show_data():
            st.subheader("Case Folding")
            st.write("Didalam tahap Case Folding, Memperkecilkan text(lower text), serta membersihkan kata yang tidak perlu seperti nomor dll")
            st.write(df['caseFolding'])

            st.subheader("Lematisasi")
            st.write("menyederhakan kata ke dalam bentuk kamus")
            st.write(df['lemmatizer'])

            st.subheader("Stemmer")
            st.write("Penguraian bentuk dari suatu kata menjadi bentuk dasar")
            st.write(df['stemmer'])

            st.subheader("Slang Word")
            st.write("Merubah kata alay menjadi kata baku")
            st.write(df["slang"])

            st.subheader("Stop Word")
            st.write("Menghapus kata yang tidak perlu")
            st.write(df["stopword"])

            st.subheader("Text Clean")
            st.write("pembersihan text terakhir, di dalam proses ini menghapus kata di bawah 3 huruf")
            st.write(df["Text_Clean"])

            st.subheader("Split Text")
            st.write("membagi setiap kata")
            st.write(df["Text_Clean_split"])

            st.subheader("Polarity Count")
            st.write("hasil polarity")
            st.table(df["polarity"].value_counts())

            st.bar_chart(df["polarity"].value_counts())

            st.subheader("Polarity Tahunan")
            st.write("Menampilkan polarity setiap tahun")
            st.line_chart(data_chart)

            st.subheader("TF-IDF")
            st.write(ranking)

            colp1,colp2 = st.columns(2)

            with colp1:
                st.subheader("Top 10 Positive Words")
                st.dataframe(top_10_positive)

            with colp2:
                st.subheader("Top 10 Negative Words")
                st.dataframe(top_10_negative)
            
            data_share = {
                "Jenis Data": ["Semua Data", "Data Test", "Data Latih"],
                "Jumlah Data": [len(df), len(y_test), len(y_train)]
            }

            st.subheader("Pembagian Data")
            st.table(data_share)
            
            st.subheader("Confusion Matrix")
            fig, ax = plt.subplots()
            plot_confusion_matrix(svm, X_test, y_test, ax=ax)
            
            st.pyplot(fig)

            st.subheader("RFC Classification Report")
            st.dataframe(df_classification_report, use_container_width=True)

            st.subheader("Akurasi")
            st.info(f"Data Memiliki tingkat akurasi {accuracy}")

        show_data()

    if selected == "Sentimen Predictor File":
        st.header("Sentimen Predictor File")
        dataset = st.file_uploader("Upload Dataset", type="csv")

        if dataset is not None:
            data_raw = pd.read_csv(dataset)
            st.subheader("Row Data")
            st.write(data_raw)
            st.write(f"Panjang data: {len(data_raw)}")

            column_names = data_raw.columns.tolist()
            selected_column = st.selectbox("Pilih colum yang ingin di analisis",column_names)

            submitFile = st.button("Analisis")
            if submitFile:
                def load_proses():
                    df, hasil_positive, hasil_negative = ft.hasilFileMining(data_raw,selected_column)
                    top_10_positive, top_10_negative = ft.process_top_10_words(hasil_positive, hasil_negative)
                    ranking = ft.calculate_tfidf_ranking(df)
                    X, y = ft.process_data(df)
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
                    predic, svm, y_pred = ft.predic_SVM(X_train, X_test, y_train, y_test)

                    # Simpan laporan klasifikasi dalam variabel
                    report = classification_report(y_test, y_pred, output_dict=True)

                    # Konversi laporan menjadi DataFrame pandas
                    df_classification_report = pd.DataFrame(report).transpose()

                    
                    accuracy = f"{predic.round(2)*100}%"

                    return df, accuracy, top_10_positive, top_10_negative, ranking, X_test, y_test, y_train, y, svm, df_classification_report
                
                df, accuracy, top_10_positive, top_10_negative, ranking, X_test, y_test, y_train, y, svm, df_classification_report = load_proses()

                def show_data():
                    st.subheader("Case Folding")
                    st.write("Didalam tahap Case Folding, Memperkecilkan text(lower text), serta membersihkan kata yang tidak perlu seperti nomor dll")
                    st.write(df['caseFolding'])

                    st.subheader("Lematisasi")
                    st.write("menyederhakan kata ke dalam bentuk kamus")
                    st.write(df['lemmatizer'])

                    st.subheader("Stemmer")
                    st.write("Penguraian bentuk dari suatu kata menjadi bentuk dasar")
                    st.write(df['stemmer'])

                    st.subheader("Slang Word")
                    st.write("Merubah kata alay menjadi kata baku")
                    st.write(df["slang"])

                    st.subheader("Stop Word")
                    st.write("Menghapus kata yang tidak perlu")
                    st.write(df["stopword"])

                    st.subheader("Text Clean")
                    st.write("pembersihan text terakhir, di dalam proses ini menghapus kata di bawah 3 huruf")
                    st.write(df["Text_Clean"])

                    st.subheader("Split Text")
                    st.write("membagi setiap kata")
                    st.write(df["Text_Clean_split"])

                    st.subheader("Polarity Count")
                    st.write("hasil polarity")
                    st.table(df["polarity"].value_counts())

                    st.bar_chart(df["polarity"].value_counts())

                    st.subheader("TF-IDF")
                    st.write(ranking)

                    colp1,colp2 = st.columns(2)

                    with colp1:
                        st.subheader("Top 10 Positive Words")
                        st.dataframe(top_10_positive)

                    with colp2:
                        st.subheader("Top 10 Negative Words")
                        st.dataframe(top_10_negative)
                    
                    data_share = {
                        "Jenis Data": ["Semua Data", "Data Test", "Data Latih"],
                        "Jumlah Data": [len(df), len(y_test), len(y_train)]
                    }

                    st.subheader("Pembagian Data")
                    st.table(data_share)
                    
                    st.subheader("Confusion Matrix")
                    fig, ax = plt.subplots()
                    plot_confusion_matrix(svm, X_test, y_test, ax=ax)
                    
                    st.pyplot(fig)

                    st.subheader("RFC Classification Report")
                    st.dataframe(df_classification_report, use_container_width=True)

                    st.subheader("Akurasi")
                    st.info(f"Data Memiliki tingkat akurasi {accuracy}")

                    st.download_button(label='Download CSV',data =df.to_csv(), file_name="model_df.csv" ,mime='text/csv')

                show_data()          
            
if __name__ == "__main__":
    admin_home()    
