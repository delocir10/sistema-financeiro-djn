import streamlit as st
import pandas as pd
import io
from auth import check_password

# Verifica autenticação antes de renderizar a página
if not check_password():
    st.stop()

st.set_page_config(page_title="Projetos FTTH", page_icon="📡", layout="wide")

st.title("📡 Projetos FTTH - Estimativa e Viabilidade")
st.markdown("Calcule o CAPEX, custos de LPU, exporte a lista de materiais detalhada e veja o ROI da sua rede.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Parâmetros da Rede")
    
    st.markdown("**Cabos Principais da Rede**")
    st.caption("Adicione linhas na tabela abaixo para incluir vários tipos de cabos.")
    # Tabela dinâmica de cabos
    df_cabos_padrao = pd.DataFrame([
        {"Tipo de Cabo": "Cabo AS-80 12F", "Metragem (m)": 1000, "Preço (R$/m)": 1.83}
    ])
    
    opcoes_cabo = [
        "Cabo Drop Flat 01F", "Cabo AS-80 06F", "Cabo AS-80 12F", 
        "Cabo AS-80 24F", "Cabo AS-80 36F", "Cabo AS-80 48F", 
        "Cabo AS-80 72F", "Cabo AS-80 144F", "Outro"
    ]

    # Preços pré-definidos
    precos_tabela = {
        "Cabo Drop Flat 01F": 0.40,
        "Cabo AS-80 06F": 1.63,
        "Cabo AS-80 12F": 1.83,
        "Cabo AS-80 24F": 4.99,
        "Cabo AS-80 36F": 6.76,
        "Cabo AS-80 48F": 8.59,
        "Cabo AS-80 72F": 12.25,
        "Cabo AS-80 144F": 25.10,
        "Outro": 0.00
    }

    # Data Editor
    edited_cabos = st.data_editor(
        df_cabos_padrao,
        column_config={
            "Tipo de Cabo": st.column_config.SelectboxColumn("Tipo", options=opcoes_cabo, required=True),
            "Metragem (m)": st.column_config.NumberColumn("Metragem (m)", min_value=1, step=100, required=True),
            "Preço (R$/m)": st.column_config.NumberColumn("Preço LPU (R$/m)", min_value=0.0, step=0.1, format="%.2f")
        },
        num_rows="dynamic",
        use_container_width=True
    )
    
    # Soma de cabos e preenchimento automático do preço
    if not edited_cabos.empty:
        # Puxa o preço automático se o usuário deixou em branco (None)
        def preenche_preco(row):
            if pd.isna(row["Preço (R$/m)"]) or row["Preço (R$/m)"] == 0:
                return precos_tabela.get(row["Tipo de Cabo"], 0.0)
            return row["Preço (R$/m)"]
            
        edited_cabos["Preço (R$/m)"] = edited_cabos.apply(preenche_preco, axis=1)
        metragem_total = int(edited_cabos["Metragem (m)"].sum())
    else:
        metragem_total = 0
    
    # CTOs e CEOs
    st.markdown("---")
    col_cto, col_ceo = st.columns(2)
    with col_cto:
        qtd_cto = st.number_input("Qtd. de CTOs", min_value=0, value=5, step=1)
        portas_cto = st.selectbox("Portas por CTO", [8, 16])
        preco_cto = 129.90 if portas_cto == 8 else 134.90
    with col_ceo:
        qtd_ceo = st.number_input("Qtd. de CEOs (Reserva)", min_value=0, value=1, step=1)
    
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
    
    with st.expander("⚙️ Tabela de Preços e Regras de Ferragens (Clique para ajustar)"):
        st.markdown("**Distribuição de Postes** *(Recomendado: Urbano 60/40 | Rural 40/60)*")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            perc_passagem = st.number_input("% Passagem", min_value=0, max_value=100, value=60)
        with col_p2:
            perc_ancoragem = st.number_input("% Ancoragem", min_value=0, max_value=100, value=40)
        
        st.markdown("**Mão de Obra**")
        custo_lancamento = st.number_input("Lançamento Aéreo (R$/m)", min_value=0.0, value=1.50, step=0.10, format="%.2f")
        custo_fusao = st.number_input("Fusão de Fibra (R$/un)", min_value=0.0, value=20.00, step=1.0, format="%.2f")
        custo_inst_cto = st.number_input("Instalação CTO (R$/un)", min_value=0.0, value=100.00, step=10.0, format="%.2f")
        custo_inst_ceo = st.number_input("Batimento de CEO (R$/un)", min_value=0.0, value=100.00, step=10.0, format="%.2f")
        
        st.markdown("**Materiais e OPEX**")
        preco_ceo = st.number_input("Preço da CEO (Média R$)", min_value=0.0, value=68.00, step=10.0, format="%.2f")
        preco_bap = st.number_input("Preço BAP 3 (R$)", min_value=0.0, value=9.72, format="%.2f")
        preco_alca = st.number_input("Preço Alça (R$)", min_value=0.0, value=6.00, format="%.2f")
        preco_sup_diel = st.number_input("Preço Suporte Dielétrico (R$)", min_value=0.0, value=6.40, format="%.2f")
        preco_olhal = st.number_input("Preço Olhal/SIPA (R$)", min_value=0.0, value=15.00, format="%.2f")
        preco_plaqueta = st.number_input("Preço Plaqueta (R$)", min_value=0.0, value=0.75, format="%.2f")
        distancia_postes = st.number_input("Distância média entre postes (m)", min_value=1, value=40, step=5)
        fusoes_estimadas = st.number_input("Qtd. Fusões Estimadas", min_value=0, value=((qtd_cto * 2) + (qtd_ceo * 4)), step=1)
        aluguel_poste = st.number_input("Aluguel de Poste Equatorial (R$/mês)", min_value=0.0, value=7.00, step=1.0, format="%.2f")

# -------------- CÁLCULOS -------------- #

# 1. Regra de Postes e Ferragens
qtd_total_postes = int(metragem_total / distancia_postes) if distancia_postes > 0 else 0
postes_comuns = max(0, qtd_total_postes - qtd_cto - qtd_ceo)

qtd_passagem = int(postes_comuns * (perc_passagem / 100.0))
qtd_ancoragem = postes_comuns - qtd_passagem

# Quantidades de Ferragens (Regras da LPU DJN)
qtd_bap_cto = qtd_cto * 2       # 2 baps por CTO
qtd_bap_ceo = qtd_ceo * 2       # 2 baps por CEO (reserva)
qtd_bap_passagem = qtd_passagem * 1  # 1 bap por poste de passagem
qtd_bap_ancoragem = qtd_ancoragem * 1 # 1 bap por poste de ancoragem

total_baps = qtd_bap_cto + qtd_bap_ceo + qtd_bap_passagem + qtd_bap_ancoragem
total_sup_diel = qtd_passagem
total_olhal = qtd_ancoragem + qtd_cto + qtd_ceo  # olhal para ancorar a CTO/CEO
total_alcas = (qtd_ancoragem * 2) + (qtd_cto * 2) + (qtd_ceo * 2)
total_plaquetas = qtd_total_postes + qtd_ceo # 1 por poste + 1 extra onde tem CEO/reserva

# Custo de Material
if not edited_cabos.empty:
    custo_mat_cabo = (edited_cabos["Metragem (m)"] * edited_cabos["Preço (R$/m)"]).sum()
else:
    custo_mat_cabo = 0.0

custo_mat_cto = qtd_cto * preco_cto
custo_mat_ceo = qtd_ceo * preco_ceo

custo_ferragens = (total_baps * preco_bap) + (total_sup_diel * preco_sup_diel) + (total_olhal * preco_olhal) + (total_alcas * preco_alca) + (total_plaquetas * preco_plaqueta)
total_material = custo_mat_cabo + custo_mat_cto + custo_mat_ceo + custo_ferragens

# Mão de Obra e Engenharia
custo_mo_lancamento = metragem_total * custo_lancamento
custo_mo_cto = qtd_cto * custo_inst_cto
custo_mo_ceo = qtd_ceo * custo_inst_ceo
custo_mo_fusoes = fusoes_estimadas * custo_fusao

custo_eng_desenho = (metragem_total * 0.60) if incluir_desenho else 0.0
if modo_proj_comp == "Por Metro de Cabo":
    custo_eng_comp = metragem_total * valor_proj_comp
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

opex_postes = qtd_total_postes * aluguel_poste
lucro_mensal_estimado = receita_mensal - opex_postes

payback = (capex_total / lucro_mensal_estimado) if lucro_mensal_estimado > 0 else 0
custo_por_hp = (capex_total / hp_total) if hp_total > 0 else 0

st.divider()
st.subheader("📊 Resultados de Viabilidade (CAPEX e ROI)")

def formata_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

m1, m2, m3, m4 = st.columns(4)
m1.metric("CAPEX Total (Custo Projeto)", formata_brl(capex_total))
m2.metric("Home Passed (HP)", f"{hp_total} portas")
m3.metric("Custo por HP", formata_brl(custo_por_hp))
m4.metric("Clientes Estimados", f"{clientes_estimados} assinantes", f"{tx_penetracao}% Penetração")

m5, m6, m7, m8 = st.columns(4)
m5.metric("Receita Mensal Bruta", formata_brl(receita_mensal))
m6.metric("Lucro Operacional (R. - OPEX)", formata_brl(lucro_mensal_estimado), f"- {formata_brl(opex_postes)} (Aluguel Postes)")
m7.metric("Payback Estimado", f"{payback:.1f} meses")
m8.metric("Qtd. Postes Calculados", f"{qtd_total_postes} postes")

st.divider()

# Exibição de Custos Separados (Material e Mão de Obra/Engenharia)
col_tabela1, col_tabela2 = st.columns(2)

with col_tabela1:
    st.write("### 📦 Custos de Material")
    df_mat_view = pd.DataFrame({
        "Item": ["Cabos Ópticos", "CTOs", "Caixas de Emenda (CEO)", "Ferragens e Plaquetas"],
        "Custo Total": [custo_mat_cabo, custo_mat_cto, custo_mat_ceo, custo_ferragens]
    })
    df_mat_view['Custo Total'] = df_mat_view['Custo Total'].apply(formata_brl)
    st.dataframe(df_mat_view, use_container_width=True, hide_index=True)

with col_tabela2:
    st.write("### 👷‍♂️ Custos de Serviço e Engenharia")
    df_mo_view = pd.DataFrame({
        "Atividade": [
            "Lançamento Aéreo (Infra)", 
            "Instalação CTOs", 
            "Instalação CEOs", 
            "Fusões de Fibra", 
            "Projeto KMZ / Cálculo", 
            "Projeto de Compartilhamento"
        ],
        "Custo Total": [
            custo_mo_lancamento, 
            custo_mo_cto, 
            custo_mo_ceo, 
            custo_mo_fusoes, 
            custo_eng_desenho, 
            custo_eng_comp
        ]
    })
    df_mo_view['Custo Total'] = df_mo_view['Custo Total'].apply(formata_brl)
    st.dataframe(df_mo_view, use_container_width=True, hide_index=True)

st.divider()

# Lista de Materiais e Exportação
col_list, col_exp = st.columns([3, 1])
with col_list:
    st.write("### 📥 Lista de Materiais (BOM)")
with col_exp:
    # Preparar DataFrame de Exportação
    lista_export = []
    
    # Adicionar cada cabo individualmente
    if not edited_cabos.empty:
        for _, row in edited_cabos.iterrows():
            lista_export.append({"Item": row['Tipo de Cabo'], "Quantidade": row['Metragem (m)'], "Unidade": "m", "Preço Unit.": row['Preço (R$/m)'], "Total": row['Metragem (m)'] * row['Preço (R$/m)']})
    
    # Adicionar Ativos
    lista_export.append({"Item": f"CTO {portas_cto} Portas com Splitter", "Quantidade": qtd_cto, "Unidade": "un", "Preço Unit.": preco_cto, "Total": custo_mat_cto})
    lista_export.append({"Item": "CEO / Caixa de Emenda", "Quantidade": qtd_ceo, "Unidade": "un", "Preço Unit.": preco_ceo, "Total": custo_mat_ceo})
    
    # Adicionar Ferragens Detalhadas
    lista_export.append({"Item": "BAP 3 (Total somado)", "Quantidade": total_baps, "Unidade": "un", "Preço Unit.": preco_bap, "Total": total_baps * preco_bap})
    lista_export.append({"Item": "Suporte Dielétrico (Postes de Passagem)", "Quantidade": total_sup_diel, "Unidade": "un", "Preço Unit.": preco_sup_diel, "Total": total_sup_diel * preco_sup_diel})
    lista_export.append({"Item": "SIPA / Suporte Olhal", "Quantidade": total_olhal, "Unidade": "un", "Preço Unit.": preco_olhal, "Total": total_olhal * preco_olhal})
    lista_export.append({"Item": "Alças Pré-Formadas", "Quantidade": total_alcas, "Unidade": "un", "Preço Unit.": preco_alca, "Total": total_alcas * preco_alca})
    lista_export.append({"Item": "Plaquetas de Identificação", "Quantidade": total_plaquetas, "Unidade": "un", "Preço Unit.": preco_plaqueta, "Total": total_plaquetas * preco_plaqueta})
    
    df_export = pd.DataFrame(lista_export)
    
    # Gerar CSV
    csv_buffer = io.StringIO()
    df_export.to_csv(csv_buffer, index=False, decimal=',', sep=';')
    csv_data = csv_buffer.getvalue().encode("utf-8-sig") # utf-8-sig permite que o Excel entenda os acentos corretamente
    
    st.download_button(
        label="📥 Baixar Excel / CSV",
        data=csv_data,
        file_name="lista_de_materiais_ftth.csv",
        mime="text/csv",
        use_container_width=True
    )

# Exibe a tabela formatada na tela
st.dataframe(df_export.style.format({"Preço Unit.": "R$ {:.2f}", "Total": "R$ {:.2f}"}), use_container_width=True)

