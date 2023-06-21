import streamlit as st
import function.config as db
import streamlit_authenticator as stauth

def user_update(username):
    st.header("Update User")
    response = db.get_user(username) 
    user_data = response 
    name = user_data["name"]
    
    username_user = st.text_input("Username :" , username , disabled=True)
    name_user = st.text_input("Masukan Nama :", name)
    password_user = st.text_input("Masukan Password :", type="password")
    hashed_passwords = stauth.Hasher([password_user]).generate()
    hashed_password = hashed_passwords[0]

    button_update = st.button("Update")

    if button_update:
        if name_user == "" or password_user == "":
            st.warning("Tolong isikan datanya")
        else :
            if username != username_user:
                st.warning('Anda tidak bisa mengubah punya orang lain!')
            else:
                db.update_user(username,updates={"name": name_user, "password" : hashed_password})
                st.success("Pembaharuan Berhasil")

if __name__ == "__main__":
    user_update()