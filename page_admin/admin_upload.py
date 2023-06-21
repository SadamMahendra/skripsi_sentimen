# import streamlit as st
# import function.config as db
# import pandas as pd

# def admin_upload():
#     st.header("Upload tester")

#     data = db.db_drive.get("model_df.csv")
#     df = pd.read_csv(data)

#     st.write(df)

#     file = st.file_uploader("masukan file", type="csv")
#     submit = st.button("lohe")

#     if submit:
#         db.db_drive.put(file.name, data=file)

# if __name__ == "__main__":
#     admin_upload()