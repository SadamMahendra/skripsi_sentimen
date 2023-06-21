import streamlit as st
from streamlit_option_menu import option_menu
import function.config as db
import streamlit_authenticator as stauth

def lvl(level):
    if level == "admin":
        return 0
    if level =="user":
        return 1

def admin_register(username):
    selected = option_menu(None, ["Add","Update","Delete"], 
                icons=['person-fill-add',"person-fill-gear","person-fill-dash"], 
                menu_icon="cast", default_index=0, orientation="horizontal")
    
    if selected == "Add":
        st.subheader("Add User")
        inputUser = st.text_input("Masukan Username")
        inputName = st.text_input("Masukan Nama")
        inputPassword = st.text_input("Masukan Password", type="password")
        inputAuth = st.selectbox("Masukan Role", ["admin","user"])
        hashed_passwords = stauth.Hasher([inputPassword]).generate()
        hashed_password = hashed_passwords[0]
        buttonS = st.button("register")
        if buttonS:
            db.insert_user(inputUser,inputName,hashed_password,inputAuth)
            
    if selected == "Update":
        users = db.fetch_all_users()
        data = {
            "Username": [user["key"] for user in users],
            "Name": [user["name"] for user in users],
            "Role": [user["level"] for user in users]
        }
        st.subheader("Update User")
        st.dataframe(data,use_container_width=True)

        usernames = list(set(data["Username"]))
        selected_username = st.selectbox("Pilih Username", usernames)
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
        button_update = st.button("Update")

        if button_update:
            if name == "" or password == "" or level == "":
                st.warning("Tolong Masukan Semua Datanya")
            else :
                db.update_user(selected_username,updates={"name" : name, "password" : hashed_password , "level" : level})
                st.experimental_rerun()

    if selected == "Delete":
        users = db.fetch_all_users()
        data = {
            "Username": [user["key"] for user in users],
            "Name": [user["name"] for user in users],
            "Role": [user["level"] for user in users]
        }
        st.subheader("Delete User")
        st.dataframe(data,use_container_width=True)

        usernames = list(set(data["Username"]))
        selected_username = st.selectbox("Pilih Username", usernames)
 
        button_delete = st.button("Delete")

        if button_delete:
            if selected_username == username:
                st.warning("maaf anda tidak bisa mendelete anda sendiri")
            else:
                db.delete_user(selected_username)
                st.experimental_rerun()

if __name__ == "__main__":
    admin_register()