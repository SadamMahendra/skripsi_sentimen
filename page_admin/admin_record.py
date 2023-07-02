import streamlit as st
import pandas as pd
from datetime import date
import io

# buffer to use for excel writer
buffer = io.BytesIO()

@st.cache_data
def dataJnt ():
    return pd.read_csv("./data/model_df.csv")

def admin_record():  
    df = dataJnt()

    df['at'] = pd.to_datetime(df['at'])
    df = df.sort_values('at')
    tahun = df['at'].dt.year.unique().tolist()
    bulan = list(range(1, 13))

    st.header("📖 Report",
              help="Halaman untuk melihat laporan mingguan atau bulanan")
    st.markdown("---")

    TipeLaporan = st.radio(
    "Pemilihan Laporan Bedasarkan :",
    ('Bulanan', 'Mingguan'))

    if TipeLaporan == "Bulanan":
        col1,col2 = st.columns(2)
        # Tanggal
        with col1:
            bulan_filter = st.selectbox('Bulan:', bulan)

        # Bulan
        with col2:
            tahun_filter = st.selectbox('Tahun:', tahun,index=1 )

        # Filtering dataframe
        filtered_df = df[
            (df['at'].dt.year == tahun_filter) &
            (df['at'].dt.month == bulan_filter)
        ]
            
        if filtered_df.empty:
            st.write("Tidak ada data untuk bulan dan tahun yang dipilih.")
        else:
            filter_dataframe = filtered_df[['Text_Clean','at','polarity_score','polarity']]
            with st.expander("Data Report"):
                st.write(filter_dataframe.reset_index(drop=True))
            # Menghitung jumlah kemunculan 'negatif' dan 'positif' berdasarkan bulan
            polarity_counts = filtered_df['polarity'].value_counts()
            total_count = polarity_counts.sum()

            if 'negative' in polarity_counts and 'positive' in polarity_counts:
                if polarity_counts['negative'] > polarity_counts['positive']:
                    st.warning(f"Polarity yang dominan dari {total_count} Kalimat adalah NEGATIF")
                elif polarity_counts['positive'] > polarity_counts['negative']:
                    st.success(f"Polarity yang dominan adalah dari {total_count} Kalimat adalah POSITIF")
                else:
                    st.info("Jumlah kemunculan 'negatif' dan 'positif' sama")
            
            #csv
            st.download_button(label='🖨️ Download CSV',data =filter_dataframe.to_csv()
                               ,file_name=f'Data Bulan {bulan_filter} Tahun {tahun_filter}.csv'
                               ,mime='text/csv')
            
            #excel
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                filter_dataframe.to_excel(writer, sheet_name='Sheet1', index=False)

                st.download_button(
                    label="🖨️ Download Excel",
                    data=buffer,
                    file_name=f'Data Bulan {bulan_filter} Tahun {tahun_filter}.xlsx',
                    mime='application/vnd.ms-excel'
)
    
    if TipeLaporan == "Mingguan" :
        min_date = df['at'].dt.date.min()
        max_date = df['at'].dt.date.max()

        current_date = date.today()

        # Memperbarui tanggal maksimum menjadi tanggal saat ini
        max_date = current_date

        # Menampilkan tanggal input dengan nilai default
        tanggal = st.date_input("Pilih Tanggal:", min_value=min_date, max_value=max_date, value=current_date)

        tanggal = pd.to_datetime(tanggal)

        end_date = tanggal + pd.DateOffset(days=6)
        
        filtered_df = df[(df['at'] >= tanggal) & (df['at'] <= end_date)]

        if filtered_df.empty:
            st.write("Tidak ada data Mingguan yang dipilih.")
        else:
            st.write(f"Data di ambil dari {tanggal} sampai {end_date}")

            filter_dataframe = filtered_df[['Text_Clean','at','polarity_score','polarity']]
            with st.expander("Data Report"):
                st.write(filter_dataframe.reset_index(drop=True))

            # Menghitung jumlah kemunculan 'negatif' dan 'positif' berdasarkan bulan
            polarity_counts = filtered_df['polarity'].value_counts()
            total_count = polarity_counts.sum()

            if 'negative' in polarity_counts and 'positive' in polarity_counts:
                if polarity_counts['negative'] > polarity_counts['positive']:
                    st.warning(f"Polarity yang dominan dari {total_count} Kalimat adalah NEGATIF")
                elif polarity_counts['positive'] > polarity_counts['negative']:
                    st.success(f"Polarity yang dominan adalah dari {total_count} Kalimat adalah POSITIF")
                else:
                    st.info("Jumlah kemunculan 'negatif' dan 'positif' sama")
                        
            #csv
            st.download_button(label='🖨️ Download CSV',data =filter_dataframe.to_csv(), file_name="Data Mingguan.csv" ,mime='text/csv')
            
            #excel
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                filter_dataframe.to_excel(writer, sheet_name='Sheet1', index=False)

                st.download_button(
                    label="🖨️ Download Excel",
                    data=buffer,
                    file_name=f'Data Mingguan.xlsx',
                    mime='application/vnd.ms-excel')
                
if __name__ == "__main__":
    admin_record()