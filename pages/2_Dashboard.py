import streamlit as st
import pandas as pd
from datetime import date
from database import get_lancamentos
from utils import format_currency
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import check_password, check_admin

if not check_password():
    st.stop()

check_admin()

st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")

st.title("📈 Dashboard Mensal")

# Seletores de Mês e Ano
col_m, col_a, _ = st.columns([2, 2, 8])
with col_m:
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    mes_atual = date.today().month
    mes_selecionado_nome = st.selectbox("Mês", list(meses.values()), index=mes_atual-1)
    mes_selecionado = list(meses.keys())[list(meses.values()).index(mes_selecionado_nome)]
    
with col_a:
    ano_atual = date.today().year
    anos = list(range(ano_atual - 2, ano_atual + 3))
    ano_selecionado = st.selectbox("Ano", anos, index=anos.index(ano_atual))

# Carrega os dados
df = get_lancamentos(mes=mes_selecionado, ano=ano_selecionado)

if df.empty:
    st.info(f"Nenhum lançamento encontrado para {mes_selecionado_nome}/{ano_selecionado}.")
else:
    # Separa entradas e saídas
    df_entradas = df[df['tipo'] == 'Entrada']
    df_saidas = df[df['tipo'] == 'Saída']
    
    # Cálculos
    total_entradas = df_entradas['valor'].sum()
    total_saidas = df_saidas['valor'].sum()
    saldo_estimado = total_entradas - total_saidas
    
    total_receita_com_nota = df_entradas[df_entradas['categoria'] == 'Receita com nota']['valor'].sum()
    total_receita_sem_nota = df_entradas[df_entradas['categoria'] == 'Receita sem nota']['valor'].sum()
    total_adiantamentos = df_entradas[df_entradas['categoria'] == 'Adiantamento de cliente']['valor'].sum()
    
    total_terceiro_rpa = df_saidas[df_saidas['categoria'] == 'Terceiro com RPA']['valor'].sum()
    total_terceiro_sem_rpa = df_saidas[df_saidas['categoria'] == 'Terceiro sem RPA']['valor'].sum()
    
    # Renderiza os cards
    st.markdown("### Resumo Financeiro")
    col1, col2, col3 = st.columns(3)
    
    cor_saldo = "green" if saldo_estimado >= 0 else "red"
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Entradas</div>
            <div class="metric-value" style="color: green;">{format_currency(total_entradas)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Saídas (Despesas)</div>
            <div class="metric-value" style="color: red;">{format_currency(total_saidas)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Saldo Estimado</div>
            <div class="metric-value" style="color: {cor_saldo};">{format_currency(saldo_estimado)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detalhamentos
    st.markdown("### Detalhamento por Categoria")
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("**Entradas Específicas:**")
        st.write(f"Receitas com Nota: **{format_currency(total_receita_com_nota)}**")
        st.write(f"Receitas sem Nota: **{format_currency(total_receita_sem_nota)}**")
        st.write(f"Adiantamentos: **{format_currency(total_adiantamentos)}**")
        
    with col5:
        st.markdown("**Saídas Específicas:**")
        st.write(f"Terceiros com RPA: **{format_currency(total_terceiro_rpa)}**")
        st.write(f"Terceiros sem RPA: **{format_currency(total_terceiro_sem_rpa)}**")
        
    st.markdown("---")
    
    # Pendências Críticas
    st.markdown("### ⚠️ Pendências Críticas")
    df_pendencias = df[df['pendencia_critica'] == 1]
    
    if df_pendencias.empty:
        st.success("Tudo certo! Nenhuma pendência crítica para envio à contabilidade neste mês.")
    else:
        st.warning("Existem lançamentos com pendências críticas que precisam ser resolvidos antes do envio (dia 25)!")
        
        # Formatando para exibição
        df_exibir_pendencias = df_pendencias[['data', 'descricao', 'valor', 'categoria', 'motivo_pendencia']].copy()
        df_exibir_pendencias['valor'] = df_exibir_pendencias['valor'].apply(lambda x: format_currency(x))
        df_exibir_pendencias.columns = ['Data', 'Descrição', 'Valor', 'Categoria', 'Motivo da Pendência']
        
        st.dataframe(df_exibir_pendencias, use_container_width=True, hide_index=True)
