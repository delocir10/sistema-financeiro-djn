import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import database
from auth import check_password, check_admin

if not check_password():
    st.stop()

# Essa página só pode ser acessada pelo dono (admin)
check_admin()

st.set_page_config(page_title="Gerenciar Assinaturas", page_icon="🔐", layout="wide")

st.title("🔐 Gestão de Assinantes (SaaS)")
st.markdown("Crie logins para engenheiros e libere o acesso após o pagamento do PIX.")

# ================================
# 1. Tabela de Usuários Ativos
# ================================
st.subheader("👥 Engenheiros e Assinantes")
df_users = database.get_all_users()

if not df_users.empty:
    # Formata a exibição
    df_view = df_users[['id', 'username', 'role', 'expires_at']].copy()
    
    # Lógica de status
    hoje = datetime.now().date()
    status_list = []
    for d in df_view['expires_at']:
        if isinstance(d, str):
            venc = datetime.strptime(d, "%Y-%m-%d").date()
        else:
            venc = d
            
        if venc < hoje:
            status_list.append("🔴 Vencido / Bloqueado")
        else:
            status_list.append("🟢 Ativo")
            
    df_view['Status'] = status_list
    df_view.columns = ['ID', 'Usuário', 'Nível de Acesso', 'Vencimento', 'Status']
    
    st.dataframe(df_view, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum usuário encontrado.")

st.markdown("---")

col1, col2 = st.columns(2)

# ================================
# 2. Renovar Assinatura (Liberar PIX)
# ================================
with col1:
    st.subheader("✅ Liberar Acesso (Confirmar PIX)")
    st.markdown("Adiciona +30 dias de acesso a um usuário bloqueado.")
    
    if not df_users.empty:
        # Filtra apenas quem não é admin para aparecer na lista de renovação
        df_eng = df_users[df_users['role'] != 'admin']
        if not df_eng.empty:
            usuario_renovar = st.selectbox("Selecione o Usuário para Renovar", df_eng['username'].tolist())
            
            if st.button("Renovar +30 Dias", use_container_width=True):
                user_info = df_eng[df_eng['username'] == usuario_renovar].iloc[0]
                
                # Se já estiver vencido, 30 dias a partir de hoje. Se ainda estiver ativo, soma 30 dias no vencimento atual.
                if isinstance(user_info['expires_at'], str):
                    venc_atual = datetime.strptime(user_info['expires_at'], "%Y-%m-%d").date()
                else:
                    venc_atual = user_info['expires_at']
                    
                nova_data = max(hoje, venc_atual) + timedelta(days=30)
                
                try:
                    database.renew_user(user_info['id'], nova_data)
                    st.success(f"Acesso liberado! Novo vencimento: {nova_data.strftime('%d/%m/%Y')}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao renovar: {e}")
        else:
            st.info("Nenhum engenheiro cadastrado para renovar.")

# ================================
# 3. Criar Novo Usuário
# ================================
with col2:
    st.subheader("➕ Cadastrar Novo Engenheiro")
    
    with st.form("form_novo_user"):
        novo_user = st.text_input("Nome de Usuário (Ex: joao.engenharia)")
        nova_senha = st.text_input("Senha Inicial", type="password")
        
        # Como padrão, o sistema te dá acesso a cadastrar só engenheiros (para evitar falhas de segurança)
        st.info("Nível de Acesso: Engenheiro (Restrito a Projetos FTTH)")
        
        # Permite dar uns dias grátis de teste ou já criar ativo
        dias_validade = st.number_input("Dias Iniciais de Acesso (Ex: 30 para ativo, 0 para bloqueado)", min_value=0, value=30, step=1)
        
        if st.form_submit_button("Criar Usuário", use_container_width=True):
            if novo_user and nova_senha:
                data_exp = hoje + timedelta(days=dias_validade)
                # Tenta adicionar no BD
                sucesso = database.add_user(novo_user, nova_senha, "engenheiro", data_exp)
                if sucesso:
                    st.success(f"Usuário {novo_user} criado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro: Esse nome de usuário já existe!")
            else:
                st.warning("Preencha o usuário e a senha.")

