import sqlite3
import hashlib


def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

ligacao = sqlite3.connect("willkadasa.db")
ligacao.execute("PRAGMA foreign_keys = ON;")
cursor = ligacao.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS professores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER,
    numero TEXT,
    FOREIGN KEY (email_id) REFERENCES email(id),
    FOREIGN KEY (disciplinas_id) REFERENCES disciplinas(id)
)         
""")  

cursor.execute("""
CREATE TABLE IF NOT EXISTS disciplinas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL                        
)            
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS email (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email_principal TEXT UNIQUE NOT NULL,
    email_recuperacao TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL 
    FOREIGN KEY (professores_id) REFERENCES professores (id)                                        
)
""")



ligacao.commit()

ligacao.close()

print("Base de dados e tabelas foram criados com sucesso")










