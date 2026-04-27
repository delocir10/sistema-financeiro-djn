import streamlit as st
from datetime import date
from database import add_lancamento
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import check_password

if not check_password():
    st.stop()

st.set_page_config(page_title="Novo Lançamento", page_icon="📝", layout="wide")

st.title("📝 Lançamento Rápido")
st.markdown("Registre entradas e saídas da conta PJ.")

# Categorias
CATEGORIAS = [
    "Receita com nota",
    "Receita sem nota",
    "Adiantamento de cliente",
    "Reembolso",
    "Empréstimo de sócio",
    "Empréstimo de terceiro",
    "Compra de material",
    "Combustível/deslocamento",
    "Terceiro com RPA",
    "Terceiro sem RPA",
    "Retirada de lucro",
    "Pró-labore",
    "Taxas bancárias/contabilidade",
    "Outros"
]

with st.form("form_lancamento"):
    col1, col2 = st.columns(2)
    
    with col1:
        data_lancamento = st.date_input("Data do Lançamento", value=date.today(), format="DD/MM/YYYY")
        tipo = st.selectbox("Tipo da Movimentação", ["Entrada", "Saída"])
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f", step=10.0)
        categoria = st.selectbox("Categoria", CATEGORIAS)
        
    with col2:
        descricao = st.text_input("Descrição do Lançamento")
        pessoa_empresa = st.text_input("Pessoa/Empresa (CPF/CNPJ e/ou Nome)")
        observacao = st.text_area("Observação (Opcional)")
        
    st.markdown("### Documentação")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        tem_nf = st.radio("Possui Nota Fiscal?", ["Não", "Sim"]) == "Sim"
    with col4:
        tem_rpa = st.radio("Possui RPA?", ["Não", "Sim"]) == "Sim"
    with col5:
        tem_comprovante = st.radio("Possui Comprovante?", ["Sim", "Não"]) == "Sim"
        
    submit_button = st.form_submit_button("Salvar Lançamento", use_container_width=True)

if submit_button:
    if not descricao:
        st.error("Por favor, preencha a descrição.")
    else:
        # Avaliação de Regras Automáticas e Pendências
        pendencia = False
        motivo_pendencia = []
        avisos = []
        
        # 1. Se entrada for “Receita sem nota”, marcar como pendência crítica.
        if tipo == "Entrada" and categoria == "Receita sem nota":
            pendencia = True
            motivo_pendencia.append("Receita recebida sem emissão de Nota Fiscal.")
            
        # 2. Se saída para CPF e sem RPA, marcar como pendência crítica.
        # Simplificando a verificação de "CPF" pelo tipo de categoria ou texto
        if tipo == "Saída" and categoria == "Terceiro sem RPA":
            pendencia = True
            motivo_pendencia.append("Pagamento a terceiro sem emissão de RPA.")
            
        # 3. Se compra de material sem nota, marcar pendência.
        if categoria == "Compra de material" and not tem_nf:
            pendencia = True
            motivo_pendencia.append("Compra de material sem Nota Fiscal.")
            
        # 4. Avisos e sugestões:
        # Se entrada de CPF para PJ (simplificado se contem CPF ou pela categoria)
        if tipo == "Entrada" and (categoria not in ["Receita com nota", "Receita sem nota", "Adiantamento de cliente"]):
            avisos.append("Dica: Se foi entrada de pessoa física, verifique se não é 'Empréstimo de terceiro' ou 'Empréstimo de sócio'.")
            
        # Se saída para sócio, sugerir “reembolso”, “pró-labore” ou “distribuição de lucro”
        if tipo == "Saída" and categoria not in ["Reembolso", "Pró-labore", "Retirada de lucro", "Empréstimo de sócio"] and "socio" in pessoa_empresa.lower():
            avisos.append("Dica: Para pagamentos ao sócio, use 'Reembolso', 'Pró-labore' ou 'Retirada de lucro'.")
            
        # Se adiantamento de cliente, avisar que precisa vincular depois à nota ou contrato.
        if categoria == "Adiantamento de cliente":
            avisos.append("Aviso: Adiantamento registrado. Lembre-se de vincular a uma Nota Fiscal ou Contrato futuramente.")
            
        # Converte lista de motivos para string
        motivo_str = " | ".join(motivo_pendencia) if pendencia else ""
        
        try:
            # Salva no banco de dados
            add_lancamento(
                data=data_lancamento,
                descricao=descricao,
                valor=valor,
                tipo=tipo,
                pessoa_empresa=pessoa_empresa,
                categoria=categoria,
                observacao=observacao,
                nf=tem_nf,
                rpa=tem_rpa,
                comprovante=tem_comprovante,
                pendencia_critica=pendencia,
                motivo_pendencia=motivo_str
            )
            st.success("Lançamento salvo com sucesso!")
            
            # Exibe os alertas e pendências na tela para o usuário ver na hora
            if pendencia:
                st.error(f"⚠️ PENDÊNCIA CRÍTICA REGISTRADA: {motivo_str}")
                
            for aviso in avisos:
                st.info(f"💡 {aviso}")
                
        except Exception as e:
            st.error(f"Erro ao salvar lançamento: {e}")
