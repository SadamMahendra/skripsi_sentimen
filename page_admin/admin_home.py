import streamlit as st
import pandas as pd
import function.functions as ft
from sklearn.model_selection import train_test_split
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix , ConfusionMatrixDisplay , classification_report



@st.cache_data
def data_raw_jnt ():
    return pd.read_csv("./data/Scrapped_J&T.csv")

def admin_home():
    st.header("🏡 Home",
              help="Halaman untuk Menampilkan Data Visual Atau Halaman Sentiment Predictor untuk file")
    st.markdown("---")

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
        st.info(f"Panjang data: {len(data_raw)}")

        @st.cache_data(show_spinner="Data Cache untuk proses sedang disiapkan")
        def load_proses():
            # Cleaning Data
            df, hasil_positive, hasil_negative = ft.hasilFileMining(data_raw, 'content')

            # Top 10 Positif dan Negatif
            top_10_positive, top_10_negative = ft.process_top_10_words(hasil_positive, hasil_negative)

            #WordCloud
            wordcloud_positive = ft.wordcloud_positive(df)
            wordcloud_negative = ft.wordcloud_negative(df)

            # TF-IDF
            X, y = ft.process_data(df)

            # Membagi data menjadi data latih dan data uji
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)

            # Melakukan prediksi dengan menggunakan model SVM
            predic, svm, y_pred = ft.predic_SVM(X_train, X_test, y_train, y_test)

            # laporan klasifikasi
            report = classification_report(y_test, y_pred, output_dict=True)

            # Konversi laporan menjadi DataFrame pandas
            df_classification_report = pd.DataFrame(report).transpose()

            # Menghitung akurasi prediksi
            accuracy = f"{predic.round(2) * 100}%"

            # Polarity Tahunan
            data_chart = ft.Polarity_Tahunan(df)

            return df, accuracy, wordcloud_positive, wordcloud_negative, svm, top_10_positive, top_10_negative, X, data_chart, y_test, y_train, y_pred, df_classification_report

        df, accuracy, wordcloud_positive, wordcloud_negative,svm, top_10_positive, top_10_negative, X, data_chart, y_test, y_train, y_pred, df_classification_report = load_proses()

        @st.cache_data
        def show_data():
            st.subheader("Case Folding")
            st.write("Memperkecilkan teks dengan mengubahnya menjadi huruf kecil (lower text)")
            st.write(df['caseFolding'].head(11))

            st.subheader("Cleansing")
            st.write("Membersihkan teks dari karakter yang tidak diinginkan seperti huruf besar, angka, dan spasi")
            st.write(df["cleansing"].head(11))

            st.subheader("Stemmer")
            st.write("Menguraikan kata-kata dalam teks menjadi bentuk dasarnya")
            st.write(df['stemmer'].head(11))

            st.subheader("Slang Word")
            st.write("Mengganti kata-kata yang tidak baku menjadi kata baku")
            st.write(df["slang"].head(11))

            st.subheader("Stop Word")
            st.write("Menghapus kata-kata yang umum dan tidak memberikan makna signifikan dalam teks")
            st.write(df["stopword"].head(11))

            st.subheader("Text Clean")
            st.write("Melakukan pembersihan teks terakhir dengan menghapus kata-kata yang terdiri dari kurang dari 3 huruf")
            st.write(df["Text_Clean"].head(11))

            st.subheader("Split Text")
            st.write("Membagi setiap kata dalam teks menjadi unit terpisah")
            st.write(df["Text_Clean_split"].head(11))

            st.subheader("Polarity Count")
            st.write("Menampilkan hasil polaritas (sentimen) dari teks")
            st.table(df["polarity"].value_counts())

            with st.expander("Polarity", expanded=True):
                st.bar_chart(df["polarity"].value_counts())

            with st.expander("Polarity Tahunan", expanded=True):
                st.line_chart(data_chart)

            with st.expander("wordcloud", expanded=True):
                colw1,colw2 = st.columns(2)
                with colw1:
                    st.pyplot(wordcloud_positive)

                with colw2:
                    st.pyplot(wordcloud_negative)

            st.subheader("TF-IDF")
            with st.expander("Output TF-IDF",expanded=True):
                st.text(X[0:2])

            colp1,colp2 = st.columns(2)

            with colp1:
                st.subheader("Top 10 Positive Words")
                st.dataframe(top_10_positive,hide_index=True)

            with colp2:
                st.subheader("Top 10 Negative Words")
                st.dataframe(top_10_negative,hide_index=True)
            
            data_share = {
                "Jenis Data": ["Semua Data", "Data Test", "Data Latih"],
                "Jumlah Data": [len(df), len(y_test), len(y_train)]
            }

            st.subheader("Pembagian Data")
            st.dataframe(data_share, use_container_width=True)
            
            st.subheader("Classification Report")
            st.dataframe(df_classification_report, use_container_width=True)
            
            st.subheader("Confusion Matrix")
            cm = confusion_matrix(y_test,y_pred)

            #menampilkan Confusion Matrix  
            fig, ax = plt.subplots()
            ConfusionMatrixDisplay(cm,display_labels=svm.classes_).plot(ax=ax)  
            st.pyplot(fig)

            TP = cm[1,1]
            TN = cm[0,0]
            FN = cm[0,1]
            FP = cm[1,0]
            st.dataframe({ "Tipe Data" : ["True Negative (TN)","True Positive (TP)","False Negative (FN)","False Positive (FP)"],
                            "Hasil" : [TN,TP,FN,FP]
            },use_container_width=True)
            accuracy_cm = (TP + TN) / (TP + TN + FP + FN)
            result_accuracy = round(accuracy_cm,3)*100

            st.subheader("Akurasi")
            with st.expander("Rumus"):
                st.latex(r'''
                \text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
                ''')
                st.latex(r'''
                \text{Accuracy} = \frac{%d + %d}{%d + %d + %d + %d} = %s\%%
                ''' % (TP, TN, TP, TN, FP, FN, result_accuracy))

            st.info(f"Data Memiliki tingkat akurasi {accuracy}")

        show_data()
        
    if selected == "Sentimen Predictor File":
        st.header("Sentimen Predictor File")
        dataset = st.file_uploader("Upload Dataset", type="csv")

        if dataset is not None:
            data_raw = pd.read_csv(dataset)
            st.subheader("Row Data")
            st.write(data_raw)
            st.info(f"Panjang data: {len(data_raw)}")

            column_names = data_raw.columns.tolist()
            selected_column = st.selectbox("Pilih colum yang ingin di analisis",column_names)

            submitFile = st.button("Analisis")
            if submitFile:
                def load_proses():
                    # Cleaning Data
                    df, hasil_positive, hasil_negative = ft.hasilFileMining(data_raw, selected_column)

                    # Top 10 Positif dan Negatif
                    top_10_positive, top_10_negative = ft.process_top_10_words(hasil_positive, hasil_negative)

                    #WordCloud
                    wordcloud_positive = ft.wordcloud_positive(df)
                    wordcloud_negative = ft.wordcloud_negative(df)

                    # TF-IDF
                    X, y = ft.process_data(df)

                    # Membagi data menjadi data latih dan data uji
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)

                    # Melakukan prediksi dengan menggunakan model SVM
                    predic, svm, y_pred = ft.predic_SVM(X_train, X_test, y_train, y_test)

                    # laporan klasifikasi
                    report = classification_report(y_test, y_pred, output_dict=True)

                    # Konversi laporan menjadi DataFrame pandas
                    df_classification_report = pd.DataFrame(report).transpose()

                    # Menghitung akurasi prediksi
                    accuracy = f"{predic.round(2) * 100}%"

                    return df, accuracy, wordcloud_positive, wordcloud_negative, svm, top_10_positive, top_10_negative, X, y_test, y_train, y_pred, df_classification_report

                df, accuracy, wordcloud_positive, wordcloud_negative,svm, top_10_positive, top_10_negative, X, y_test, y_train, y_pred, df_classification_report = load_proses()

                def show_data():
                    st.subheader("Case Folding")
                    st.write("Memperkecilkan teks dengan mengubahnya menjadi huruf kecil (lower text)")
                    st.write(df['caseFolding'].head(11))

                    st.subheader("Cleansing")
                    st.write("Membersihkan teks dari karakter yang tidak diinginkan seperti huruf besar, angka, dan spasi")
                    st.write(df["cleansing"].head(11))

                    st.subheader("Stemmer")
                    st.write("Menguraikan kata-kata dalam teks menjadi bentuk dasarnya")
                    st.write(df['stemmer'].head(11))

                    st.subheader("Slang Word")
                    st.write("Mengganti kata-kata yang tidak baku menjadi kata baku")
                    st.write(df["slang"].head(11))

                    st.subheader("Stop Word")
                    st.write("Menghapus kata-kata yang umum dan tidak memberikan makna signifikan dalam teks")
                    st.write(df["stopword"].head(11))

                    st.subheader("Text Clean")
                    st.write("Melakukan pembersihan teks terakhir dengan menghapus kata-kata yang terdiri dari kurang dari 3 huruf")
                    st.write(df["Text_Clean"].head(11))

                    st.subheader("Split Text")
                    st.write("Membagi setiap kata dalam teks menjadi unit terpisah")
                    st.write(df["Text_Clean_split"].head(11))

                    st.subheader("Polarity Count")
                    st.write("Menampilkan hasil polaritas (sentimen) dari teks")
                    st.table(df["polarity"].value_counts())

                    with st.expander("Polarity", expanded=True):
                        st.bar_chart(df["polarity"].value_counts())

                    with st.expander("wordcloud", expanded=True):
                        colw1,colw2 = st.columns(2)
                        with colw1:
                            st.pyplot(wordcloud_positive)

                        with colw2:
                            st.pyplot(wordcloud_negative)

                    st.subheader("TF-IDF")
                    with st.expander("Output TF-IDF",expanded=True):
                        st.text(X[0:2])

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
                    st.dataframe(data_share, use_container_width=True)

                    st.subheader("Classification Report")
                    st.dataframe(df_classification_report, use_container_width=True)
                    
                    st.subheader("Confusion Matrix")
                    cm = confusion_matrix(y_test,y_pred)

                    #menampilkan Confusion Matrix  
                    fig, ax = plt.subplots()
                    ConfusionMatrixDisplay(cm,display_labels=svm.classes_).plot(ax=ax)  
                    st.pyplot(fig)

                    TP = cm[1,1]
                    TN = cm[0,0]
                    FN = cm[0,1]
                    FP = cm[1,0]
                    st.dataframe({ "Tipe Data" : ["True Negative (TN)","True Positive (TP)","False Negative (FN)","False Positive (FP)"],
                                  "Hasil" : [TN,TP,FN,FP]
                    },use_container_width=True)
                    
                    accuracy_cm = (TP + TN) / (TP + TN + FP + FN)
                    result_accuracy = round(accuracy_cm,3)*100

                    st.subheader("Akurasi")
                    with st.expander("Rumus"):
                        st.latex(r'''
                        \text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
                        ''')
                        st.latex(r'''
                        \text{Accuracy} = \frac{%d + %d}{%d + %d + %d + %d} = %s\%%
                        ''' % (TP, TN, TP, TN, FP, FN, result_accuracy))

                    st.info(f"Data Memiliki tingkat akurasi {accuracy}")

                    st.download_button(label='Download CSV',data =df.to_csv(), file_name="model_df.csv" ,mime='text/csv')

                show_data()          
            
if __name__ == "__main__":
    admin_home()    
