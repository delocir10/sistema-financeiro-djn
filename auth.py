import streamlit as st

def check_password():
    """Retorna `True` se o usuário digitou a senha correta."""

    def password_entered():
        """Checa se a senha e usuário estão corretos."""
        if (
            st.session_state["username"] == st.secrets["credentials"]["username"]
            and st.session_state["password"] == st.secrets["credentials"]["password"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não mantém a senha guardada
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Interface de Login
    st.markdown("## 🔒 Acesso Restrito")
    st.markdown("Por favor, faça o login para acessar o Sistema Financeiro.")
    
    st.text_input("Usuário", key="username")
    st.text_input("Senha", type="password", key="password")
    
    if st.button("Entrar", on_click=password_entered, use_container_width=True):
        pass

    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Usuário ou senha incorretos")
        
    return False
