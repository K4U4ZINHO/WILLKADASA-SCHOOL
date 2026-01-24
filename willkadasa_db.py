import sqlite3
import hashlib

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

conn = sqlite3.connect("willkadasa.db")
conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()

# Tabela de emails (login)
cursor.execute("""
CREATE TABLE IF NOT EXISTS email (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email_principal TEXT UNIQUE NOT NULL,
    email_recuperacao TEXT,
    senha_hash TEXT NOT NULL
);
""")

# Tabela de disciplinas
cursor.execute("""
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);
""")

# Tabela de professores (sem FKs por enquanto)
cursor.execute("""
CREATE TABLE IF NOT EXISTS professores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER,
    numero TEXT
);
""")

conn.commit()
conn.close()

print("Banco criado com sucesso!")