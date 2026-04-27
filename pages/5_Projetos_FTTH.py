import streamlit as st
import pandas as pd
from auth import check_password

# Verifica autenticação antes de renderizar a página
if not check_password():
    st.stop()

st.set_page_config(page_title="Projetos FTTH", page_icon="📡", layout="wide")

st.title("📡 Projetos FTTH - Estimativa e Viabilidade")
st.markdown("Calcule rapidamente o CAPEX, custos de LPU, Home Passed (HP) e o ROI do seu projeto de expansão.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Parâmetros da Rede")
    metragem = st.number_input("Metragem Estimada (m)", min_value=0, value=1000, step=100)
    
    tipo_cabo = st.selectbox(
        "Tipo de Cabo Principal", 
        [
            "Cabo AS-80 06F (R$ 1,63/m)", 
            "Cabo AS-80 12F (R$ 1,83/m)", 
            "Cabo AS-80 24F (R$ 4,99/m)",
            "Cabo Drop Flat 01F (R$ 0,40/m)"
        ]
    )
    # Extrai o preço pela opção escolhida
    if "06F" in tipo_cabo: preco_cabo = 1.63
    elif "12F" in tipo_cabo: preco_cabo = 1.83
    elif "24F" in tipo_cabo: preco_cabo = 4.99
    else: preco_cabo = 0.40
    
    qtd_cto = st.number_input("Quantidade de CTOs", min_value=0, value=5, step=1)
    portas_cto = st.selectbox("Portas por CTO", [8, 16])
    preco_cto = 129.90 if portas_cto == 8 else 134.90
    
    qtd_ceo = st.number_input("Quantidade de Caixas de Emenda (CEO)", min_value=0, value=1, step=1)
    
    st.markdown("---")
    st.markdown("**Engenharia e Concessionária**")
    incluir_desenho = st.checkbox("Incluir Desenho e Cálculo de Potência (R$ 0,60/m)", value=True)
    modo_proj_comp = st.selectbox("Projeto de Compartilhamento de Postes", ["Não incluir", "Por Metro de Cabo", "Valor Fixo / Diária"])
    
    if modo_proj_comp == "Por Metro de Cabo":
        valor_proj_comp = st.number_input("Valor por Metro (R$/m)", min_value=0.0, value=0.60, step=0.10, format="%.2f")
    elif modo_proj_comp == "Valor Fixo / Diária":
        valor_proj_comp = st.number_input("Valor Fixo Total (R$)", min_value=0.0, value=1500.00, step=100.0, format="%.2f")
    else:
        valor_proj_comp = 0.0

with col2:
    st.subheader("💰 Parâmetros de Negócio")
    tx_penetracao = st.slider("Taxa de Penetração Estimada (%)", 1, 100, 30, help="Qual a % de ocupação esperada da rede?")
    ticket_medio = st.number_input("Ticket Médio Mensal (R$)", min_value=0.0, value=99.90, step=10.0, format="%.2f")
    
    with st.expander("⚙️ Tabela de Preços (LPU) - Clique para ajustar"):
        st.markdown("**Mão de Obra**")
        custo_lancamento = st.number_input("Lançamento Aéreo (R$/m)", min_value=0.0, value=1.50, step=0.10, format="%.2f")
        custo_fusao = st.number_input("Fusão de Fibra (R$/un)", min_value=0.0, value=20.00, step=1.0, format="%.2f")
        custo_inst_cto = st.number_input("Instalação CTO (R$/un)", min_value=0.0, value=100.00, step=10.0, format="%.2f")
        custo_inst_ceo = st.number_input("Batimento de CEO (R$/un)", min_value=0.0, value=100.00, step=10.0, format="%.2f")
        
        st.markdown("**Materiais e Outros**")
        preco_ceo = st.number_input("Preço da CEO (Média R$)", min_value=0.0, value=68.00, step=10.0, format="%.2f")
        custo_ferragem_poste = st.number_input("Ferragem Média por Poste (R$)", min_value=0.0, value=30.00, step=5.0, format="%.2f", help="Kit contendo Alça, BAP, Suporte, Isolador")
        distancia_postes = st.number_input("Distância média entre postes (m)", min_value=1, value=40, step=5)
        fusoes_estimadas = st.number_input("Qtd. Fusões Estimadas", min_value=0, value=((qtd_cto * 2) + (qtd_ceo * 4)), step=1)
        aluguel_poste = st.number_input("Aluguel de Poste Equatorial (R$/mês)", min_value=0.0, value=7.00, step=1.0, format="%.2f", help="Custo mensal de OPEX por poste para abater do lucro")

# -------------- CÁLCULOS -------------- #

# Material
custo_mat_cabo = metragem * preco_cabo
custo_mat_cto = qtd_cto * preco_cto
custo_mat_ceo = qtd_ceo * preco_ceo

qtd_postes = int(metragem / distancia_postes) if distancia_postes > 0 else 0
custo_mat_ferragens = qtd_postes * custo_ferragem_poste

total_material = custo_mat_cabo + custo_mat_cto + custo_mat_ceo + custo_mat_ferragens

# Mão de Obra e Engenharia
custo_mo_lancamento = metragem * custo_lancamento
custo_mo_cto = qtd_cto * custo_inst_cto
custo_mo_ceo = qtd_ceo * custo_inst_ceo
custo_mo_fusoes = fusoes_estimadas * custo_fusao

custo_eng_desenho = (metragem * 0.60) if incluir_desenho else 0.0
if modo_proj_comp == "Por Metro de Cabo":
    custo_eng_comp = metragem * valor_proj_comp
elif modo_proj_comp == "Valor Fixo / Diária":
    custo_eng_comp = valor_proj_comp
else:
    custo_eng_comp = 0.0

total_mo = custo_mo_lancamento + custo_mo_cto + custo_mo_ceo + custo_mo_fusoes + custo_eng_desenho + custo_eng_comp

# Resultados de Negócio
capex_total = total_material + total_mo
hp_total = qtd_cto * portas_cto
clientes_estimados = int(hp_total * (tx_penetracao / 100.0))
receita_mensal = clientes_estimados * ticket_medio

opex_postes = qtd_postes * aluguel_poste
lucro_mensal_estimado = receita_mensal - opex_postes

payback = (capex_total / lucro_mensal_estimado) if lucro_mensal_estimado > 0 else 0
custo_por_hp = (capex_total / hp_total) if hp_total > 0 else 0

st.divider()
st.subheader("📊 Resultados de Viabilidade (CAPEX e ROI)")

# Formatadores para moeda BRL
def formata_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

# Exibição de Métricas Principais
m1, m2, m3, m4 = st.columns(4)
m1.metric("CAPEX Total (Custo Projeto)", formata_brl(capex_total))
m2.metric("Home Passed (HP)", f"{hp_total} portas")
m3.metric("Custo por HP", formata_brl(custo_por_hp))
m4.metric("Clientes Estimados", f"{clientes_estimados} assinantes", f"{tx_penetracao}% de Penetração")

m5, m6, m7, m8 = st.columns(4)
m5.metric("Receita Mensal Bruta", formata_brl(receita_mensal))
m6.metric("Lucro Operacional Estimado", formata_brl(lucro_mensal_estimado), f"- {formata_brl(opex_postes)} (Aluguel Postes)")
m7.metric("Payback Estimado", f"{payback:.1f} meses")
m8.metric("Total Mão de Obra e Eng.", formata_brl(total_mo))

st.divider()

# Tabelas Detalhadas
col_tabela1, col_tabela2 = st.columns(2)

with col_tabela1:
    st.write("### 📦 Detalhamento de Material")
    df_mat = pd.DataFrame({
        "Item": ["Cabo Óptico Principal", "CTOs", "Caixas de Emenda (CEO)", "Ferragens (Kits/Poste)"],
        "Quantidade": [f"{metragem}m", f"{qtd_cto} un", f"{qtd_ceo} un", f"{qtd_postes} postes"],
        "Custo Total": [custo_mat_cabo, custo_mat_cto, custo_mat_ceo, custo_mat_ferragens]
    })
    
    # Formata a coluna monetária
    df_mat['Custo Total'] = df_mat['Custo Total'].apply(formata_brl)
    st.dataframe(df_mat, use_container_width=True, hide_index=True)

with col_tabela2:
    st.write("### 👷‍♂️ Detalhamento de Mão de Obra e Eng.")
    df_mo = pd.DataFrame({
        "Atividade": ["Lançamento Aéreo", "Instalação CTOs", "Batimento/Instalação CEOs", "Fusões de Fibra", "Engenharia (Desenho + Comp.)"],
        "Quantidade": [f"{metragem}m", f"{qtd_cto} un", f"{qtd_ceo} un", f"{fusoes_estimadas} un", "1 Projeto"],
        "Custo Total": [custo_mo_lancamento, custo_mo_cto, custo_mo_ceo, custo_mo_fusoes, (custo_eng_desenho + custo_eng_comp)]
    })
    
    # Formata a coluna monetária
    df_mo['Custo Total'] = df_mo['Custo Total'].apply(formata_brl)
    st.dataframe(df_mo, use_container_width=True, hide_index=True)
