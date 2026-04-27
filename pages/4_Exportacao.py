import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
from database import get_lancamentos, get_orcamentos
from utils import format_currency
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import check_password

if not check_password():
    st.stop()

st.set_page_config(page_title="Exportação", page_icon="📤", layout="wide")

st.title("📤 Exportação para Contabilidade")
st.markdown("Gere o arquivo Excel consolidado do mês para enviar à Agilize ou ao seu contador.")

col_m, col_a, _ = st.columns([2, 2, 8])
with col_m:
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    mes_atual = date.today().month
    mes_selecionado_nome = st.selectbox("Mês para Exportação", list(meses.values()), index=mes_atual-1)
    mes_selecionado = list(meses.keys())[list(meses.values()).index(mes_selecionado_nome)]
    
with col_a:
    ano_atual = date.today().year
    anos = list(range(ano_atual - 2, ano_atual + 3))
    ano_selecionado = st.selectbox("Ano para Exportação", anos, index=anos.index(ano_atual))

df_lancamentos = get_lancamentos(mes=mes_selecionado, ano=ano_selecionado)
df_orcamentos = get_orcamentos()

if st.button("Gerar Arquivo Excel", use_container_width=True):
    if df_lancamentos.empty:
        st.warning("Não há lançamentos no período selecionado.")
    else:
        # Prepara os dados para o Excel
        # 1. Todos os lançamentos
        df_export_lancamentos = df_lancamentos.drop(columns=['id'])
        
        # 2. Resumo por categoria
        df_resumo = df_lancamentos.groupby(['tipo', 'categoria'])['valor'].sum().reset_index()
        df_resumo = df_resumo.sort_values(by=['tipo', 'valor'], ascending=[True, False])
        
        # 3. Pendências
        df_pendencias = df_lancamentos[df_lancamentos['pendencia_critica'] == 1].drop(columns=['id'])
        
        # 4. Orçamentos (todos, como é um histórico geral)
        df_export_orcamentos = df_orcamentos.drop(columns=['id']) if not df_orcamentos.empty else pd.DataFrame()
        
        # Criação do arquivo Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export_lancamentos.to_excel(writer, sheet_name='Lançamentos', index=False)
            df_resumo.to_excel(writer, sheet_name='Resumo_Categorias', index=False)
            df_pendencias.to_excel(writer, sheet_name='Pendências_Críticas', index=False)
            if not df_export_orcamentos.empty:
                df_export_orcamentos.to_excel(writer, sheet_name='Histórico_Orçamentos', index=False)
                
        # O processamento do Excel deve terminar antes de pegarmos o valor
        processed_data = output.getvalue()
        
        # Nome do arquivo sugerido
        file_name = f"Financeiro_DJN_{mes_selecionado_nome}_{ano_selecionado}.xlsx"
        
        st.success("Arquivo gerado com sucesso!")
        st.download_button(
            label="Baixar Arquivo Excel",
            data=processed_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
