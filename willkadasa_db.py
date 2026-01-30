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
    senha_hash TEXT NOT NULL,
    tipo TEXT NOT NULL,
    email_principal TEXT UNIQUE NOT NULL,
    email_recuperacao TEXT   
    
)
""")

# Tabela de disciplinas
cursor.execute("""
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
""")

# Tabela de professores (Verificar se as chaves estrangeiras estão a funcionar)
cursor.execute("""
CREATE TABLE IF NOT EXISTS professores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER,
    numero TEXT
    email_id INTEGER UNIQUE, 
    FOREIGN KEY (email_id) REFERENCES email(id) ON DELETE SET NULL 
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skwd_aluno TEXT UNIQUE NOT NULL,
    turma_id TEXT NOT NULL,
    nome TEXT NOT NULL,        
    email_id INTEGER UNIQUE, 
    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
    FOREIGN KEY (email_id) REFERENCES email(id) ON DELETE SET NULL
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
CREATE TABLE IF NOT EXISTS questoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL   
    disciplina_id INTEGER,
    FOREIGN KEY (disciplina_id) REFERENCES disciplina(id) ON DELETE SET NULL  
)          
""")





#cursorexames
#cursorsubmissão
#cursorrespostas
#melhorar a base das questões(adicionar ordem e pontuação)


#def classificar(pontuacao):
#    if pontuacao >= 75:
#        return "Ouro"
#    elif pontuacao >= 50:
#        return "Prata"
#    else:
#       return "Bronze"


#for a in alunos:
#a["nivel"] = classificar(a["pontuacao"])


#Elite>Mestre>Diamante>Platina>Ouro>Prata>Bronze
conn.commit()
conn.close()

print("Banco criado com sucesso!")