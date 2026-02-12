from flask import Blueprint, render_template, session, flash, url_for, redirect, request
# Importamos as funções que gerenciam a conexão híbrida
from willkadasa_db import db_query, db_execute

aluno_bp = Blueprint("aluno", __name__, url_prefix="/aluno")

# --- DASHBOARD PRINCIPAL ---
@aluno_bp.route("/dashboard")
def dashboard_aluno():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))

    # Busca a turma_id do aluno logado usando a função db_query
    aluno_data = db_query("""
        SELECT turma_id FROM alunos 
        WHERE email_id = (SELECT id FROM email WHERE LOWER(email_principal) = LOWER(?))
    """, (email,), one=True)
    
    id_turma = aluno_data['turma_id'] if aluno_data else None

    return render_template("home_aluno.html", id_turma=id_turma)

# --- VER TURMA ---
@aluno_bp.route("/minha_turma")
def ver_turma_aluno():
    return redirect(url_for('ver_turma_aluno_sessao.ver_turma_aluno'))

# --- VER NOTAS ---
@aluno_bp.route("/ver_notas_aluno/<int:id_turma>")
def ver_notas_aluno(id_turma):
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))
    
    # Busca o nome do exame e a nota que o aluno tirou
    notas = db_query("""
        SELECT e.titulo AS teste, s.pontuacao_total AS nota
        FROM submissoes_exame s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN email em ON a.email_id = em.id
        WHERE em.email_principal = ? AND a.turma_id = ?
        ORDER BY s.data_submissao DESC
    """, (email, id_turma))
    
    return render_template("ver_notas_aluno.html", notas=notas, id_turma=id_turma)

# --- REALIZAR TESTE ---
@aluno_bp.route("/realizar_teste/<int:id_exame>", methods=["GET", "POST"])
def realizar_teste(id_exame):
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))

    if request.method == "POST":
        # 1. Pegar ID do aluno
        aluno_row = db_query("SELECT a.id FROM alunos a JOIN email e ON a.email_id = e.id WHERE e.email_principal = ?", (email,), one=True)
        aluno_id = aluno_row["id"]

        # 2. Buscar as questões e respostas corretas para este exame
        questoes_gabarito = db_query("""
            SELECT q.id, q.resposta_correta, eq.pontuacao 
            FROM questoes q
            JOIN exame_questoes eq ON q.id = eq.questao_id
            WHERE eq.exame_id = ?
        """, (id_exame,))

        # 3. Criar a submissão inicial
        # Nota: O PostgreSQL não usa datetime('now'), ele usa CURRENT_TIMESTAMP
        # O db_execute vai cuidar disso se você ajustou o willkadasa_db
        db_execute("""
            INSERT INTO submissoes_exame (exame_id, aluno_id, data_submissao, estado)
            VALUES (?, ?, CURRENT_TIMESTAMP, 'corrigido')
        """, (id_exame, aluno_id))
        
        # Pegamos o ID da última submissão inserida
        # No Postgres, isso costuma ser feito com RETURNING id, mas para simplificar:
        last_sub = db_query("SELECT id FROM submissoes_exame WHERE aluno_id = ? ORDER BY id DESC", (aluno_id,), one=True)
        submissao_id = last_sub['id']

        pontuacao_total_aluno = 0
        
        # 4. Processar respostas e calcular nota
        for q in questoes_gabarito:
            resposta_aluno = request.form.get(f"q{q['id']}")
            pontuacao_atribuida = 0
            
            if resposta_aluno and str(resposta_aluno).strip().upper() == str(q['resposta_correta']).strip().upper():
                pontuacao_atribuida = q['pontuacao']
                pontuacao_total_aluno += pontuacao_atribuida

            # Salvar resposta individual
            db_execute("""
                INSERT INTO respostas (submissao_id, questao_id, resposta_dada, pontuacao_atribuida)
                VALUES (?, ?, ?, ?)
            """, (submissao_id, q['id'], resposta_aluno, pontuacao_atribuida))

        # 5. Atualizar a nota final
        db_execute("UPDATE submissoes_exame SET pontuacao_total = ? WHERE id = ?", (pontuacao_total_aluno, submissao_id))

        flash(f"Teste enviado! Sua nota foi: {pontuacao_total_aluno}", "success")
        return redirect(url_for("testes_pendentes_aluno_sessao.testes_pendentes_aluno"))

    # --- LÓGICA DO GET (Carregar Questões) ---
    exame = db_query("SELECT titulo FROM exames WHERE id = ?", (id_exame,), one=True)
    questoes = db_query("""
        SELECT q.id, q.enunciado, q.tipo 
        FROM questoes q
        JOIN exame_questoes eq ON q.id = eq.questao_id
        WHERE eq.exame_id = ?
        ORDER BY eq.ordem ASC
    """, (id_exame,))

    return render_template("realizar_teste.html", exame=exame, questoes=questoes, id_exame=id_exame)

@aluno_bp.route("/recuperar_senha")
def recuperar_senha():
    return render_template("recuperar_senha.html")