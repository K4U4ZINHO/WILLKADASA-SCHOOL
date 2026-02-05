from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

notas_gerais_bp = Blueprint("notas_gerais", __name__, url_prefix="/notas")

def get_db_connection():
    conn = sqlite3.connect("willkadasa.db")
    conn.row_factory = sqlite3.Row 
    return conn

@notas_gerais_bp.route("/notas_gerais/<int:id_turma>")
def notas_gerais(id_turma):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Busca alunos (garantindo que pegamos o email_id)
    cursor.execute("""
        SELECT id, nome, email_id 
        FROM alunos 
        WHERE turma_id = ?
    """, (id_turma,))
    alunos = cursor.fetchall()

    notas_por_aluno = {}

    for aluno in alunos:
        # 2. Busca as notas
        # DICA: Verifique se o nome da tabela é 'submissoes_exame' ou 'submissao_exame'
        cursor.execute("""
            SELECT e.titulo, COALESCE(s.pontuacao_total, 0) as nota
            FROM submissoes_exame s
            JOIN exames e ON s.exame_id = e.id
            WHERE s.aluno_id = ?
        """, (aluno['id'],))
        
        # ... dentro do loop for aluno in alunos:
        
        # ... dentro do loop for aluno in alunos:
        resultado = cursor.fetchall()
        
        # MUDANÇA AQUI: Usar o ID do aluno como chave (convertido para string)
        notas_por_aluno[str(aluno['id'])] = [dict(row) for row in resultado]
        # MUDANÇA AQUI: Usar o ID do aluno como chave (convertido para string)
    conn.close()
    
    # DEBUG: Olhe o seu terminal do VS Code quando abrir a página. 
    # Se aparecer {}, o problema está no banco de dados (aluno_id não bate).
    print(f"DEBUG NOTAS: {notas_por_aluno}")
    
    return render_template("notas_gerais.html", 
        alunos=alunos, 
        notas_por_aluno=notas_por_aluno,
        id_turma=id_turma)