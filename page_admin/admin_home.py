import streamlit as st
import pandas as pd
import function.functions as ft
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
import pickle
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, plot_confusion_matrix


#import model
pickle_in = open('./data/model.pkl', 'rb')
svm = pickle.load(pickle_in)

def process_data(df):
    df['Text_Clean'] = df['Text_Clean'].astype(str)
    tfidf = TfidfVectorizer()
    ulasan = df['Text_Clean'].values.tolist()
    tfidf_vect = tfidf.fit(ulasan)
    X = tfidf_vect.transform(ulasan)
    y = df['polarity']
    return X, y

def calculate_tfidf_ranking(df):
    max_features = len(df)

    tf_idf = TfidfVectorizer(max_features=max_features, binary=True)
    tfidf_mat = tf_idf.fit_transform(df["Text_Clean"]).toarray()

    terms = tf_idf.get_feature_names_out()

    sums = tfidf_mat.sum(axis=0)

    data = []
    for col, term in enumerate(terms):
        data.append((term, sums[col]))

    ranking = pd.DataFrame(data, columns=['term', 'rank'])
    ranking.sort_values('rank', ascending=False, inplace=True)

    return ranking

def prediction(X_train, X_test, y_train, y_test):
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    score = metrics.accuracy_score(y_test, y_pred)
    return score

@st.cache_data
def data_raw_jnt ():
    return pd.read_csv("./data/Scrapped_J&T.csv")

@st.cache_data
def dataJnt ():
    return pd.read_csv("./data/model_df.csv")

def admin_home():
    selected = option_menu(None, ["Data Visualisasi","Sentimen Predictor File"], 
        icons=['bar-chart-fill',"file-earmark-plus"], 
        menu_icon="cast", default_index=0, orientation="horizontal")
    
    if selected == "Data Visualisasi":
        data = dataJnt()
        data_raw = data_raw_jnt()

        st.header("Proses Data")
        st.write("Memperlihatkan Pre Processing yang ada di dalam dataset JnT")
        
        st.subheader("Raw Data")
        st.write("Berisikan data yang belum di olah")
        st.write(data_raw)
        
        X, y = process_data(data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
        predic = prediction(X_train, X_test, y_train, y_test).round(2)
        y_pred = svm.predict(X_test)

        #menampilkan grafik line tentang polarity pertahun
        data['at'] = pd.to_datetime(data['at'])
        data['tahun'] = data['at'].dt.year
   
        # Menghitung jumlah kalimat negatif dan positif per tahun sampai tahun terakhir dalam dataframe
        tahun_terakhir = data['tahun'].max()
        df_filtered = data[data['tahun'] <= tahun_terakhir]
        jumlah_negatif = df_filtered[df_filtered['polarity'] == 'negative'].groupby('tahun').size().reindex(range(df_filtered['tahun'].min(), tahun_terakhir+1), fill_value=0)
        jumlah_positif = df_filtered[df_filtered['polarity'] == 'positive'].groupby('tahun').size().reindex(range(df_filtered['tahun'].min(), tahun_terakhir+1), fill_value=0)

        # Membuat grafik menggunakan st.line_chart()
        data_chart = pd.DataFrame({
            'negative': jumlah_negatif,
            'positive': jumlah_positif
        })

        st.subheader("Case Folding")
        st.write("Didalam tahap Case Folding, Memperkecilkan text(lower text), serta membersihkan kata yang tidak perlu seperti nomor dll")
        st.write(data['caseFolding'])

        st.subheader("Lematisasi")
        st.write("menyederhakan kata ke dalam bentuk kamus")
        st.write(data['lemmatizer'])

        st.subheader("Stemmer")
        st.write("Penguraian bentuk dari suatu kata menjadi bentuk dasar")
        st.write(data['stemmer'])

        st.subheader("Slang Word")
        st.write("Merubah kata alay menjadi kata baku")
        st.write(data["slang"])

        st.subheader("Stop Word")
        st.write("Menghapus kata yang tidak perlu")
        st.write(data["stop_word"])

        st.subheader("Text Clean")
        st.write("pembersihan text terakhir, di dalam proses ini menghapus kata di bawah 3 huruf")
        st.write(data["Text_Clean"])

        st.subheader("Split Text")
        st.write("membagi setiap kata")
        st.write(data["Text_Clean_split"])

        st.subheader("Polarity Count")
        st.write("hasil polarity")
        st.table(data["polarity"].value_counts())

        st.bar_chart(data["polarity"].value_counts())

        st.subheader("Polarity Tahunan")
        st.write("Menampilkan polarity setiap tahun")
        st.line_chart(data_chart)

        st.subheader("TF-IDF")
        ranking = calculate_tfidf_ranking(data)
        st.write(ranking)

        st.subheader("Confusion Matrix")
        fig, ax = plt.subplots()
        plot_confusion_matrix(svm, X_test, y_test, ax=ax)
        
        st.pyplot(fig)

        st.subheader("Akurasi")
        accuracy = accuracy_score(y_test, y_pred).round(2)
        st.info(f"Data Memiliki tingkat akurasi {accuracy * 100}%")

    if selected == "Sentimen Predictor File":
        st.header("Sentimen Predictor File")
        dataset = st.file_uploader("Upload Dataset", type="csv")

        if dataset is not None:
            df = pd.read_csv(dataset)
            st.subheader("Row Data")
            st.write(df)
            st.write(f"Panjang data: {len(df)}")

            column_names = df.columns.tolist()
            selected_column = st.selectbox("Pilih colum yang ingin di analisis",column_names)

            submitFile = st.button("Analisis")
            if submitFile:
                cleaned_data, polarity, hasil = ft.hasilFileMining(df, selected_column)
                polarity_counts = polarity.value_counts()
                X, y = process_data(df)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
                predic = prediction(X_train, X_test, y_train, y_test).round(2)
                ranking = calculate_tfidf_ranking(df)
                top_10_positive, top_10_negative = ft.process_top_10_words(df,hasil)

                st.subheader("Clean Text")
                st.write(cleaned_data)

                st.subheader("Polarity Counts")
                st.bar_chart(polarity_counts)

                colp3,colp4 = st.columns(2)

                st.subheader("TF-IDF")
                st.write(ranking)

                st.subheader("Confusion Matrix")
                fig, ax = plt.subplots()
                plot_confusion_matrix(svm, X_test, y_test, ax=ax)
                
                st.pyplot(fig)

                st.subheader("Akurasi")
                st.info(f"Data Memiliki tingkat akurasi {predic*100}%")

                st.download_button(label='Download CSV',data =df.to_csv(), file_name="model_df.csv" ,mime='text/csv')
                
                with colp3:
                    st.subheader("Top 10 Positive Words")
                    st.dataframe(top_10_positive)
                
                with colp4:
                    st.subheader("Top 10 Negative Words")
                    st.dataframe(top_10_negative)
                
            
if __name__ == "__main__":
    admin_home()    