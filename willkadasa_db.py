import os
import sqlite3
import psycopg2
import psycopg2.extras

# Configuração do caminho para o SQLite (local)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "willkadasa.db")

def get_db():
    """Retorna uma conexão com PostgreSQL (se DATABASE_URL existir) ou SQLite."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        # Conexão PostgreSQL (Render)
        return psycopg2.connect(db_url, sslmode='require')
    else:
        # Conexão SQLite (Local)
        conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

def db_query(sql, params=(), one=False):
    """Executa uma consulta e retorna os resultados."""
    conn = get_db()
    if isinstance(conn, sqlite3.Connection):
        cur = conn.execute(sql, params)
        result = cur.fetchone() if one else cur.fetchall()
    else:
        # No Postgres, usamos DictCursor para poder acessar por nome de coluna: row['nome']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql.replace("?", "%s"), params)
        result = cur.fetchone() if one else cur.fetchall()
        cur.close()
    conn.commit()
    conn.close()
    return result

def db_execute(sql, params=()):
    """Executa um comando (INSERT, UPDATE, DELETE) sem retornar nada."""
    conn = get_db()
    if isinstance(conn, sqlite3.Connection):
        conn.execute(sql, params)
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute(sql.replace("?", "%s"), params)
        conn.commit()
        cur.close()
    conn.close()

def inicializar_banco():
    """Cria todas as tabelas necessárias no banco de dados."""
    conn = get_db()
    
    # Schema principal (Escrito em sintaxe PostgreSQL)
    schema_sql = """
        CREATE TABLE IF NOT EXISTS email (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            tipo TEXT NOT NULL,
            email_principal TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS questoes (
            id SERIAL PRIMARY KEY,
            enunciado TEXT NOT NULL,
            tipo TEXT,
            resposta_correta TEXT
        );

        CREATE TABLE IF NOT EXISTS disciplinas (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS turmas (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            ano INTEGER NOT NULL,
            curso TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS professores (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            idade INTEGER,
            numero TEXT,
            email_id INTEGER UNIQUE REFERENCES email(id) ON DELETE SET NULL,
            data_nascimento TEXT,
            telefone TEXT,
            email_secundario TEXT,
            disciplinas TEXT
        );

        CREATE TABLE IF NOT EXISTS alunos (
            id SERIAL PRIMARY KEY,
            skwd_aluno TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL,
            email_id INTEGER UNIQUE REFERENCES email(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS exames (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            data_hora_inicio TEXT NOT NULL,
            duracao_minutos INTEGER NOT NULL CHECK (duracao_minutos > 0),
            criado_por INTEGER REFERENCES professores(id) ON DELETE SET NULL,
            turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS exame_questoes (
            id SERIAL PRIMARY KEY,
            exame_id INTEGER NOT NULL REFERENCES exames(id) ON DELETE CASCADE,
            questao_id INTEGER NOT NULL REFERENCES questoes(id) ON DELETE CASCADE,
            pontuacao REAL NOT NULL,
            ordem INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS submissoes_exame (
            id SERIAL PRIMARY KEY,
            exame_id INTEGER NOT NULL REFERENCES exames(id) ON DELETE CASCADE,
            aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
            data_submissao TEXT,
            pontuacao_total REAL,
            estado TEXT
        );

        CREATE TABLE IF NOT EXISTS respostas (
            id SERIAL PRIMARY KEY,
            submissao_id INTEGER NOT NULL REFERENCES submissoes_exame(id) ON DELETE CASCADE,
            questao_id INTEGER NOT NULL REFERENCES questoes(id) ON DELETE CASCADE,
            resposta_dada TEXT,
            pontuacao_atribuida REAL
        );
    """

    if isinstance(conn, sqlite3.Connection):
        # Converte sintaxe Postgres para SQLite em tempo real
        conn.executescript(
            schema_sql.replace("SERIAL", "INTEGER PRIMARY KEY AUTOINCREMENT").replace("REAL", "FLOAT")
        )
        conn.commit()
    else:
        # Executa no Postgres
        cur = conn.cursor()
        cur.execute(schema_sql)
        conn.commit()
        cur.close()
    
    conn.close()
    print(" Banco de Dados (Híbrido) sincronizado!")