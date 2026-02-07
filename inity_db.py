import psycopg2

# COLE SUA URL COMPLETA ENTRE AS ASPAS ABAIXO
DATABASE_URL = "SUA_URL_EXTERNAL_AQUI"

def inicializar_banco():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        
        # Lista de comandos para criar suas tabelas
        comandos = [
            "CREATE TABLE IF NOT EXISTS email (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, senha_hash TEXT NOT NULL, tipo TEXT NOT NULL, email_principal TEXT UNIQUE NOT NULL)",
            "CREATE TABLE IF NOT EXISTS turmas (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, ano INTEGER NOT NULL, curso TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS professores (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, email_id INTEGER UNIQUE REFERENCES email(id) ON DELETE SET NULL)",
            "CREATE TABLE IF NOT EXISTS alunos (id SERIAL PRIMARY KEY, skwd_aluno TEXT UNIQUE NOT NULL, nome TEXT NOT NULL, turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL, email_id INTEGER UNIQUE REFERENCES email(id) ON DELETE SET NULL)"
            # Adicione os outros CREATE TABLE aqui seguindo o mesmo padrão SERIAL
        ]

        for comando in comandos:
            cursor.execute(comando)
            
        conn.commit()
        print("✅ Sucesso! Tabelas criadas no PostgreSQL do Render.")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    inicializar_banco()