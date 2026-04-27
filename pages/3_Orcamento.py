import streamlit as st
from database import add_orcamento, get_orcamentos
from utils import format_currency
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import check_password

if not check_password():
    st.stop()

st.set_page_config(page_title="Calculadora de Orçamento", page_icon="🧮", layout="wide")

st.title("🧮 Calculadora de Orçamento")
st.markdown("Estime os custos e calcule o preço de venda sugerido para seus serviços.")

with st.form("form_orcamento"):
    st.subheader("Dados do Serviço")
    nome_servico = st.text_input("Nome do Serviço / Cliente")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        custo_material = st.number_input("Custo de Material (R$)", min_value=0.0, format="%.2f", step=10.0)
        horas_tecnicas = st.number_input("Horas Técnicas Estimadas", min_value=0.0, format="%.1f", step=1.0)
        
    with col2:
        custo_deslocamento = st.number_input("Custo de Deslocamento (R$)", min_value=0.0, format="%.2f", step=10.0)
        valor_hora = st.number_input("Valor da sua Hora (R$)", min_value=0.0, value=150.0, format="%.2f", step=10.0)
        
    with col3:
        valor_auxiliar = st.number_input("Valor Pago a Auxiliar (CPF) (R$)", min_value=0.0, format="%.2f", step=10.0)
        aplicar_inss_rpa = st.checkbox("Aplicar encargo estimado de INSS/RPA (20% sobre auxiliar)?", value=True)

    st.markdown("---")
    st.subheader("Margem e Impostos")
    col4, col5 = st.columns(2)
    
    with col4:
        imposto_estimado_pct = st.number_input("Imposto Estimado NF (%)", min_value=0.0, max_value=100.0, value=6.0, format="%.1f", step=0.5)
    with col5:
        margem_desejada_pct = st.number_input("Margem de Lucro Desejada (%)", min_value=0.0, max_value=100.0, value=30.0, format="%.1f", step=1.0)
        
    calcular = st.form_submit_button("Calcular e Salvar", use_container_width=True)

if calcular:
    if not nome_servico:
        st.error("Por favor, preencha o nome do serviço.")
    else:
        # Cálculos
        custo_auxiliar_total = valor_auxiliar * 1.2 if aplicar_inss_rpa else valor_auxiliar
        custo_mao_obra_propria = horas_tecnicas * valor_hora
        
        custo_direto = custo_material + custo_deslocamento + custo_auxiliar_total + custo_mao_obra_propria
        
        # Preço Sugerido (Markup/Margem por dentro)
        # Preço = Custo / (1 - Imposto - Margem)
        # Convertendo as porcentagens para decimal
        imp_dec = imposto_estimado_pct / 100.0
        marg_dec = margem_desejada_pct / 100.0
        
        divisor = 1.0 - imp_dec - marg_dec
        
        if divisor <= 0:
            st.error("A soma do imposto e da margem de lucro deve ser menor que 100%!")
        else:
            preco_sugerido = custo_direto / divisor
            
            imposto_estimado_valor = preco_sugerido * imp_dec
            margem_valor = preco_sugerido * marg_dec # Este é o lucro líquido estimado do projeto
            preco_minimo = custo_direto / (1.0 - imp_dec) # Preço que empata (0 lucro)
            
            # Exibe os resultados
            st.success("Orçamento Calculado com Sucesso!")
            
            st.markdown("### Resultados")
            r_col1, r_col2, r_col3 = st.columns(3)
            
            with r_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Custo Direto Total</div>
                    <div class="metric-value">{format_currency(custo_direto)}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with r_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Preço Mínimo (Empate)</div>
                    <div class="metric-value" style="color: #ffc107;">{format_currency(preco_minimo)}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with r_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Preço Sugerido</div>
                    <div class="metric-value" style="color: #198754;">{format_currency(preco_sugerido)}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"**Imposto Estimado (Reserva para NF):** {format_currency(imposto_estimado_valor)}")
            st.write(f"**Lucro Estimado (Sua Margem):** {format_currency(margem_valor)}")
            
            # Salvar no BD
            dados = {
                'nome_servico': nome_servico,
                'custo_material': custo_material,
                'custo_deslocamento': custo_deslocamento,
                'valor_auxiliar': valor_auxiliar,
                'aplicar_inss_rpa': aplicar_inss_rpa,
                'imposto_estimado_pct': imposto_estimado_pct,
                'margem_desejada_pct': margem_desejada_pct,
                'horas_tecnicas': horas_tecnicas,
                'valor_hora': valor_hora,
                'custo_direto': custo_direto,
                'imposto_estimado_valor': imposto_estimado_valor,
                'margem_valor': margem_valor,
                'preco_minimo': preco_minimo,
                'preco_sugerido': preco_sugerido,
                'lucro_estimado': margem_valor
            }
            try:
                add_orcamento(dados)
                st.info("Orçamento salvo no histórico.")
            except Exception as e:
                st.error(f"Erro ao salvar orçamento: {e}")

st.markdown("---")
st.subheader("Histórico de Orçamentos")
df_orc = get_orcamentos()
if not df_orc.empty:
    df_exibir = df_orc[['data_criacao', 'nome_servico', 'custo_direto', 'preco_sugerido', 'lucro_estimado']].copy()
    df_exibir['custo_direto'] = df_exibir['custo_direto'].apply(format_currency)
    df_exibir['preco_sugerido'] = df_exibir['preco_sugerido'].apply(format_currency)
    df_exibir['lucro_estimado'] = df_exibir['lucro_estimado'].apply(format_currency)
    df_exibir.columns = ['Data', 'Serviço', 'Custo Direto', 'Preço Sugerido', 'Lucro Estimado']
    st.dataframe(df_exibir, use_container_width=True, hide_index=True)
else:
    st.write("Nenhum orçamento salvo ainda.")
