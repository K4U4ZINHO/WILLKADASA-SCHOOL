from flask import Blueprint, render_template, session, redirect, url_for
# Importamos a função de consulta híbrida
from willkadasa_db import db_query

notas_gerais_bp = Blueprint("notas_gerais", __name__, url_prefix="/notas")

@notas_gerais_bp.route("/notas_gerais/<int:id_turma>")
def notas_gerais(id_turma):
    # 1. Busca alunos da turma usando db_query
    alunos = db_query("""
        SELECT id, nome, email_id 
        FROM alunos 
        WHERE turma_id = ?
    """, (id_turma,))

    notas_por_aluno = {}

    for aluno in alunos:
        # 2. Busca as notas de cada aluno
        # A função db_query já retorna uma lista de dicionários por padrão
        resultado = db_query("""
            SELECT e.titulo, COALESCE(s.pontuacao_total, 0) as nota
            FROM submissoes_exame s
            JOIN exames e ON s.exame_id = e.id
            WHERE s.aluno_id = ?
        """, (aluno['id'],))
        
        # Armazenamos usando o ID do aluno como chave (convertido para string para o Jinja2)
        notas_por_aluno[str(aluno['id'])] = resultado
    
    # DEBUG para o terminal
    print(f"DEBUG NOTAS: {notas_por_aluno}")
    
    return render_template("notas_gerais.html", 
        alunos=alunos, 
        notas_por_aluno=notas_por_aluno,
        id_turma=id_turma)