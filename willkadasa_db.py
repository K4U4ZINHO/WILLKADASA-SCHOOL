import os
import psycopg2

def inicializar_banco():
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("DATABASE_URL não configurada.")
        return

    try:
        conn = psycopg2.connect(url, sslmode='require')
        cursor = conn.cursor()
        # Comandos adaptados para PostgreSQL (SERIAL em vez de AUTOINCREMENT)
        comandos = [
            """
            CREATE TABLE IF NOT EXISTS email (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo TEXT NOT NULL,
                email_principal TEXT UNIQUE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS questoes (
                id SERIAL PRIMARY KEY,
                enunciado TEXT NOT NULL,
                tipo TEXT,
                resposta_correta TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS disciplinas (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS turmas (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                ano INTEGER NOT NULL,
                curso TEXT NOT NULL
            )
            """,
            """
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
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                skwd_aluno TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL,
                email_id INTEGER UNIQUE REFERENCES email(id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS exames (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                data_hora_inicio TEXT NOT NULL,
                duracao_minutos INTEGER NOT NULL CHECK (duracao_minutos > 0),
                criado_por INTEGER REFERENCES professores(id) ON DELETE SET NULL,
                turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL  
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS exame_questoes (
                id SERIAL PRIMARY KEY,
                exame_id INTEGER NOT NULL REFERENCES exames(id) ON DELETE CASCADE,
                questao_id INTEGER NOT NULL REFERENCES questoes(id) ON DELETE CASCADE,
                pontuacao REAL NOT NULL,
                ordem INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS submissoes_exame (
                id SERIAL PRIMARY KEY,
                exame_id INTEGER NOT NULL REFERENCES exames(id) ON DELETE CASCADE,
                aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
                data_submissao TEXT,
                pontuacao_total REAL,
                estado TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS respostas (
                id SERIAL PRIMARY KEY,
                submissao_id INTEGER NOT NULL REFERENCES submissoes_exame(id) ON DELETE CASCADE,
                questao_id INTEGER NOT NULL REFERENCES questoes(id) ON DELETE CASCADE,
                resposta_dada TEXT,
                pontuacao_atribuida REAL
            )
            """
        ]

        for comando in comandos:
            cursor.execute(comando)
            
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabelas sincronizadas via willkadasa_db!")
    except Exception as e:
        print(f"Erro no willkadasa_db: {e}")



