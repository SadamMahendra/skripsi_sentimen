import streamlit as st
from streamlit_option_menu import option_menu
import function.config as db
import streamlit_authenticator as stauth
import time

def lvl(level):
    if level == "admin":
        return 0
    if level =="user":
        return 1

def admin_register(username):
    st.header("⚙️ Account Management",
              help="Halaman untuk menambahkan, menubah, menghapus data akun")
    st.markdown("---")

    selected = option_menu(None, ["Add","Update","Delete"], 
                icons=['person-fill-add',"person-fill-gear","person-fill-dash"], 
                menu_icon="cast", default_index=0, orientation="horizontal")
    
    users = db.fetch_all_users()
    data = {
        "Username": [user["key"] for user in users],
        "Name": [user["name"] for user in users],
        "Role": [user["level"] for user in users]
    }

    st.subheader("Data Account")
    with st.expander("Data Account"):
        st.dataframe(data,use_container_width=True)
    
    if selected == "Add":
        with st.form("Add Account"):
            inputUser = st.text_input("Masukan Username")
            inputName = st.text_input("Masukan Nama")
            inputPassword = st.text_input("Masukan Password", type="password")
            inputAuth = st.selectbox("Masukan Role", ["admin","user"])
            hashed_passwords = stauth.Hasher([inputPassword]).generate()
            hashed_password = hashed_passwords[0]
            buttonS = st.form_submit_button("register")
            if buttonS:
                db.insert_user(inputUser,inputName,hashed_password,inputAuth)
                time.sleep(1)
                st.experimental_rerun()
            
    if selected == "Update":
        with st.form("Update Account"):
            usernames = list(set(data["Username"]))
            selected_username = st.selectbox("Pilih Username yang ingin di ubah", usernames)
            response = db.get_user(selected_username) 
            user_data = response 
            names = user_data["name"]
            levels = user_data['level']

            level_person = lvl(levels)

            name = st.text_input("Masukan Nama :", names)
            password = st.text_input("masukan password :" , type="password")
            hashed_passwords = stauth.Hasher([password]).generate()
            hashed_password = hashed_passwords[0]
            options = ("admin", "user")
            level = st.selectbox("Masukan Level :" ,options, level_person)
            button_update = st.form_submit_button("Update")

            if button_update:
                if name == "" or password == "" or level == "":
                    st.warning("Tolong Masukan Semua Datanya")
                else :
                    db.update_user(selected_username,updates={"name" : name, "password" : hashed_password , "level" : level})
                    time.sleep(1)
                    st.experimental_rerun()

    if selected == "Delete":
        with st.form("Delete Account"):
            usernames = list(set(data["Username"]))
            selected_username = st.selectbox("Pilih Username yang ingin di hapus", usernames)
    
            button_delete = st.form_submit_button("Delete")

            if button_delete:
                if selected_username == username:
                    st.warning("maaf anda tidak bisa mendelete anda sendiri")
                else:
                    db.delete_user(selected_username)
                    st.success(f"Berhasil mendelete data {selected_username}")
                    time.sleep(1)
                    st.experimental_rerun()

if __name__ == "__main__":
    admin_register()