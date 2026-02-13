import os
import sqlite3
import psycopg2
import psycopg2.extras

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "willkadasa.db")

def get_db():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url, sslmode='require')
    else:
        conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

def db_query(sql, params=(), one=False):
    conn = get_db()
    if isinstance(conn, sqlite3.Connection):
        cur = conn.execute(sql, params)
        result = cur.fetchone() if one else cur.fetchall()
    else:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql.replace("?", "%s"), params)
        result = cur.fetchone() if one else cur.fetchall()
        cur.close()
    conn.commit()
    conn.close()
    return result

def db_execute(sql, params=()):
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
    conn = get_db()
    
    # Schema mestre com as novas colunas incluídas
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
            resposta_correta TEXT,
            opcao_a TEXT,
            opcao_b TEXT,
            opcao_c TEXT,
            opcao_d TEXT
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
        # --- LÓGICA LOCAL (SQLite) ---
        # Tenta adicionar colunas individualmente para não quebrar bancos existentes
        colunas_questoes = ["opcao_a", "opcao_b", "opcao_c", "opcao_d"]
        for col in colunas_questoes:
            try:
                conn.execute(f"ALTER TABLE questoes ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:
                pass 

        try:
            conn.execute("ALTER TABLE exames ADD COLUMN turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL")
        except sqlite3.OperationalError:
            pass 

        conn.commit()
        
        # Sincroniza o resto do schema
        sql_formatado = schema_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        sql_formatado = sql_formatado.replace("REAL", "FLOAT")
        conn.executescript(sql_formatado)
        conn.commit()
    else:
        # --- LÓGICA PRODUÇÃO (PostgreSQL) ---
        cur = conn.cursor()
        migracoes = [
            "ALTER TABLE exames ADD COLUMN IF NOT EXISTS turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL",
            "ALTER TABLE questoes ADD COLUMN IF NOT EXISTS opcao_a TEXT",
            "ALTER TABLE questoes ADD COLUMN IF NOT EXISTS opcao_b TEXT",
            "ALTER TABLE questoes ADD COLUMN IF NOT EXISTS opcao_c TEXT",
            "ALTER TABLE questoes ADD COLUMN IF NOT EXISTS opcao_d TEXT"
        ]
        
        for sql in migracoes:
            try:
                cur.execute(sql)
                conn.commit()
            except Exception:
                conn.rollback()

        cur.execute(schema_sql)
        conn.commit()
        cur.close()
    
    conn.close()
    print("Banco de Dados (Híbrido) sincronizado com colunas de alternativas!")