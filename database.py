import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text

def get_connection():
    """Retorna uma conexão com o banco de dados PostgreSQL via Streamlit."""
    # O Streamlit pegará automaticamente do secrets.toml a chave [connections.postgresql]
    conn = st.connection("postgresql", type="sql")
    return conn

def init_db():
    """Cria as tabelas do banco de dados no PostgreSQL caso não existam."""
    conn = get_connection()
    with conn.session as s:
        # Tabela de Lançamentos
        s.execute(text('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id SERIAL PRIMARY KEY,
            data DATE NOT NULL,
            descricao TEXT NOT NULL,
            valor NUMERIC NOT NULL,
            tipo TEXT NOT NULL,
            pessoa_empresa TEXT,
            categoria TEXT NOT NULL,
            observacao TEXT,
            nf INTEGER,
            rpa INTEGER,
            comprovante INTEGER,
            pendencia_critica INTEGER DEFAULT 0,
            motivo_pendencia TEXT
        )
        '''))
        
        # Tabela de Orçamentos
        s.execute(text('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id SERIAL PRIMARY KEY,
            data_criacao DATE NOT NULL,
            nome_servico TEXT NOT NULL,
            custo_material NUMERIC,
            custo_deslocamento NUMERIC,
            custo_art NUMERIC,
            valor_auxiliar NUMERIC,
            aplicar_inss_rpa INTEGER,
            imposto_estimado_pct NUMERIC,
            margem_desejada_pct NUMERIC,
            horas_tecnicas NUMERIC,
            valor_hora NUMERIC,
            custo_direto NUMERIC,
            imposto_estimado_valor NUMERIC,
            margem_valor NUMERIC,
            preco_minimo NUMERIC,
            preco_sugerido NUMERIC,
            lucro_estimado NUMERIC
        )
        '''))
        
        # Tabela de Usuários (SaaS)
        s.execute(text('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            expires_at DATE NOT NULL
        )
        '''))
        
        # Inserir admin padrão se a tabela estiver vazia
        result = s.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
        if result == 0:
            s.execute(text('''
            INSERT INTO usuarios (username, password, role, expires_at)
            VALUES ('admin', '060622', 'admin', '2099-12-31')
            '''))
            
        s.commit()

def add_lancamento(data, descricao, valor, tipo, pessoa_empresa, categoria, observacao, nf, rpa, comprovante, pendencia_critica, motivo_pendencia):
    """Adiciona um novo lançamento ao banco de dados."""
    conn = get_connection()
    with conn.session as s:
        s.execute(text('''
        INSERT INTO lancamentos (
            data, descricao, valor, tipo, pessoa_empresa, categoria, 
            observacao, nf, rpa, comprovante, pendencia_critica, motivo_pendencia
        ) VALUES (
            :data, :descricao, :valor, :tipo, :pessoa_empresa, :categoria, 
            :observacao, :nf, :rpa, :comprovante, :pendencia_critica, :motivo_pendencia
        )
        '''), {
            "data": data.strftime("%Y-%m-%d"),
            "descricao": descricao,
            "valor": valor,
            "tipo": tipo,
            "pessoa_empresa": pessoa_empresa,
            "categoria": categoria,
            "observacao": observacao,
            "nf": int(nf),
            "rpa": int(rpa),
            "comprovante": int(comprovante),
            "pendencia_critica": int(pendencia_critica),
            "motivo_pendencia": motivo_pendencia
        })
        s.commit()

def get_lancamentos(mes=None, ano=None):
    """Retorna um DataFrame pandas com os lançamentos. Pode filtrar por mês e ano."""
    conn = get_connection()
    
    if mes and ano:
        # No PostgreSQL, usamos EXTRACT para pegar o mês e ano
        query = text("""
            SELECT * FROM lancamentos 
            WHERE EXTRACT(MONTH FROM data) = :mes 
            AND EXTRACT(YEAR FROM data) = :ano
            ORDER BY data DESC
        """)
        df = conn.query(query.text, params={"mes": mes, "ano": ano}, ttl=0)
    else:
        df = conn.query("SELECT * FROM lancamentos ORDER BY data DESC", ttl=0)
        
    return df

def delete_lancamento(id_lancamento):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM lancamentos WHERE id = :id"), {"id": id_lancamento})
        s.commit()

def add_orcamento(dados):
    """Adiciona um novo orçamento calculado."""
    conn = get_connection()
    with conn.session as s:
        s.execute(text('''
        INSERT INTO orcamentos (
            data_criacao, nome_servico, custo_material, custo_deslocamento, custo_art, valor_auxiliar,
            aplicar_inss_rpa, imposto_estimado_pct, margem_desejada_pct, horas_tecnicas,
            valor_hora, custo_direto, imposto_estimado_valor, margem_valor, preco_minimo,
            preco_sugerido, lucro_estimado
        ) VALUES (
            :data_criacao, :nome_servico, :custo_material, :custo_deslocamento, :custo_art, :valor_auxiliar,
            :aplicar_inss_rpa, :imposto_estimado_pct, :margem_desejada_pct, :horas_tecnicas,
            :valor_hora, :custo_direto, :imposto_estimado_valor, :margem_valor, :preco_minimo,
            :preco_sugerido, :lucro_estimado
        )
        '''), {
            "data_criacao": datetime.now().strftime("%Y-%m-%d"),
            "nome_servico": dados['nome_servico'],
            "custo_material": dados['custo_material'],
            "custo_deslocamento": dados['custo_deslocamento'],
            "custo_art": dados.get('custo_art', 0.0),
            "valor_auxiliar": dados['valor_auxiliar'],
            "aplicar_inss_rpa": int(dados['aplicar_inss_rpa']),
            "imposto_estimado_pct": dados['imposto_estimado_pct'],
            "margem_desejada_pct": dados['margem_desejada_pct'],
            "horas_tecnicas": dados['horas_tecnicas'],
            "valor_hora": dados['valor_hora'],
            "custo_direto": dados['custo_direto'],
            "imposto_estimado_valor": dados['imposto_estimado_valor'],
            "margem_valor": dados['margem_valor'],
            "preco_minimo": dados['preco_minimo'],
            "preco_sugerido": dados['preco_sugerido'],
            "lucro_estimado": dados['lucro_estimado']
        })
        s.commit()

def get_orcamentos():
    """Retorna um DataFrame pandas com todos os orçamentos salvos."""
    conn = get_connection()
    df = conn.query("SELECT * FROM orcamentos ORDER BY id DESC", ttl=0)
    return df

# --- Funções de Usuários (SaaS) ---

def get_user(username):
    """Retorna os dados de um usuário pelo username."""
    conn = get_connection()
    query = text("SELECT * FROM usuarios WHERE username = :username")
    df = conn.query(query.text, params={"username": username}, ttl=0)
    if not df.empty:
        return df.iloc[0].to_dict()
    return None

def get_all_users():
    """Retorna todos os usuários cadastrados."""
    conn = get_connection()
    return conn.query("SELECT * FROM usuarios ORDER BY id ASC", ttl=0)

def add_user(username, password, role, expires_at):
    """Adiciona um novo usuário ao banco."""
    conn = get_connection()
    with conn.session as s:
        # Check if exists
        result = s.execute(text("SELECT COUNT(*) FROM usuarios WHERE username = :username"), {"username": username}).scalar()
        if result > 0:
            return False # Usuário já existe
            
        s.execute(text('''
        INSERT INTO usuarios (username, password, role, expires_at)
        VALUES (:username, :password, :role, :expires_at)
        '''), {
            "username": username,
            "password": password,
            "role": role,
            "expires_at": expires_at.strftime("%Y-%m-%d")
        })
        s.commit()
    return True

def renew_user(user_id, new_expires_at):
    """Renova o acesso do usuário atualizando a data de expiração."""
    conn = get_connection()
    with conn.session as s:
        s.execute(text("UPDATE usuarios SET expires_at = :expires_at WHERE id = :id"), {
            "expires_at": new_expires_at.strftime("%Y-%m-%d"),
            "id": user_id
        })
        s.commit()

def delete_user(user_id):
    """Remove um usuário do banco."""
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM usuarios WHERE id = :id"), {"id": user_id})
        s.commit()
