import streamlit as st
from datetime import datetime
import database

def check_password():
    """Retorna `True` se o usuário digitou a senha correta e não está vencido."""

    def password_entered():
        """Checa se a senha e usuário estão corretos via banco de dados."""
        username = st.session_state["username"]
        password = st.session_state["password"]
        
        # O banco pode não estar iniciado se for a primeira vez
        try:
            database.init_db()
        except Exception:
            pass # Se já tiver iniciado, segue em frente
            
        user_data = database.get_user(username)
        
        if user_data and user_data["password"] == password:
            # Senha correta, checar validade
            today = datetime.now().date()
            # Tratamento caso expires_at venha como string ou date do postgres
            if isinstance(user_data["expires_at"], str):
                expires_at = datetime.strptime(user_data["expires_at"], "%Y-%m-%d").date()
            else:
                expires_at = user_data["expires_at"]
            
            if user_data["role"] != "admin" and expires_at < today:
                st.session_state["password_correct"] = False
                st.session_state["login_error"] = "expired"
            else:
                st.session_state["password_correct"] = True
                st.session_state["role"] = user_data["role"]
                st.session_state["logged_user"] = user_data["username"]
                st.session_state["login_error"] = None
                
            del st.session_state["password"]  # Não mantém a senha guardada
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
            st.session_state["login_error"] = "invalid"

    if st.session_state.get("password_correct", False):
        return True

    # Interface de Login
    st.markdown("## 📡 Acesso ao Sistema")
    st.markdown("Por favor, faça o login para acessar as ferramentas.")
    
    st.text_input("Usuário", key="username")
    st.text_input("Senha", type="password", key="password")
    
    if st.button("Entrar", on_click=password_entered, use_container_width=True):
        pass

    if "login_error" in st.session_state:
        if st.session_state["login_error"] == "invalid":
            st.error("😕 Usuário ou senha incorretos")
        elif st.session_state["login_error"] == "expired":
            st.error("🚫 Sua assinatura expirou!")
            st.warning("Para liberar o acesso, realize o PIX de **R$ 39,90** para a chave abaixo:\n\n**65667211000128**\n\nEnvie o comprovante para o administrador para liberação imediata da sua conta.")
            
    return False

def check_admin():
    """Bloqueia a renderização da página se o usuário não for admin."""
    if st.session_state.get("role") != "admin":
        st.error("🔒 Acesso Restrito Administrativo")
        st.warning("Seu plano de assinatura dá acesso exclusivo à aba de **Projetos FTTH**. Escolha-a no menu lateral.")
        st.stop()
