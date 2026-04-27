import streamlit as st
from database import init_db
from auth import check_password

# Configuração da página principal
st.set_page_config(
    page_title="Sistema Financeiro - DJN Engenharia",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o banco de dados se não existir
init_db()

# Verifica o login
if not check_password():
    st.stop()

# Adiciona CSS customizado para aparência profissional
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        color: white;
    }
    h1, h2, h3 {
        color: #212529;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #0d6efd;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

st.title("Bem-vindo ao Sistema Financeiro da DJN Engenharia e Telecom")
st.markdown("---")

st.markdown("""
### 📊 Controle Financeiro PJ

Utilize o menu lateral para navegar entre as funcionalidades:

- **📝 Novo Lançamento**: Registre entradas e saídas rapidamente. O sistema avisará sobre pendências e inconsistências automaticamente.
- **📈 Dashboard**: Acompanhe o fluxo de caixa, saldos e veja as pendências críticas que precisam ser enviadas para a contabilidade (Agilize) até o dia 25.
- **🧮 Calculadora de Orçamento**: Calcule os custos e o preço de venda de seus serviços, garantindo a margem desejada.
- **📤 Exportação**: Gere o arquivo Excel mensal consolidado para enviar ao seu contador.

---
*Sistema desenvolvido para uso local.*
""")
