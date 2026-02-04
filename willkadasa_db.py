import sqlite3
import hashlib

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

conn = sqlite3.connect("willkadasa.db")
conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS email (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    senha_hash TEXT NOT NULL,
    tipo TEXT NOT NULL,
    email_principal TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ano INTEGER NOT NULL,
    curso TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS professores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER,
    numero TEXT,
    email_id INTEGER UNIQUE,
    data_nascimento TEXT,
    telefone TEXT,
    email_secundario TEXT,
    disciplinas TEXT,
    FOREIGN KEY (email_id) REFERENCES email(id) ON DELETE SET NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skwd_aluno TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    turma_id INTEGER,
    email_id INTEGER UNIQUE,
    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE SET NULL,
    FOREIGN KEY (email_id) REFERENCES email(id) ON DELETE SET NULL
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS exames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    data_hora_inicio TEXT NOT NULL,
    duracao_minutos INTEGER NOT NULL CHECK (duracao_minutos > 0),
    criado_por INTEGER,
    FOREIGN KEY (criado_por) REFERENCES professores(id) ON DELETE SET NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exame_questoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exame_id INTEGER NOT NULL,
    questao_id INTEGER NOT NULL,
    pontuacao REAL NOT NULL,
    ordem INTEGER NOT NULL,
    FOREIGN KEY (exame_id) REFERENCES exames(id) ON DELETE CASCADE,
    FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS submissoes_exame (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exame_id INTEGER NOT NULL,
    aluno_id INTEGER NOT NULL,
    data_submissao TEXT,
    pontuacao_total REAL,
    estado TEXT,
    FOREIGN KEY (exame_id) REFERENCES exames(id) ON DELETE CASCADE,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submissao_id INTEGER NOT NULL,
    questao_id INTEGER NOT NULL,
    resposta_dada TEXT,
    pontuacao_atribuida REAL,
    FOREIGN KEY (submissao_id) REFERENCES submissoes_exame(id) ON DELETE CASCADE,
    FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE
)
""")

conn.commit()
conn.close()

print("Banco criado com sucesso!")
