from flask import Blueprint, render_template, session, flash, url_for, redirect, request
import sqlite3

aluno_bp = Blueprint("aluno", __name__, url_prefix="/aluno")

def get_db_connection():
    conn = sqlite3.connect("willkadasa.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- DASHBOARD PRINCIPAL ---
@aluno_bp.route("/dashboard")
def dashboard_aluno():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca a turma_id do aluno logado
    cursor.execute("""
        SELECT turma_id FROM alunos 
        WHERE email_id = (SELECT id FROM email WHERE LOWER(email_principal) = LOWER(?))
    """, (email,))
    
    aluno_data = cursor.fetchone()
    id_turma = aluno_data['turma_id'] if aluno_data else None
    conn.close()

    return render_template("home_aluno.html", id_turma=id_turma)

# --- VER TURMA ---
@aluno_bp.route("/minha_turma")
def ver_turma_aluno():
    # Esta rota pode ser usada se você não estiver usando o blueprint separado 'ver_turma_aluno_sessao'
    return redirect(url_for('ver_turma_aluno_sessao.ver_turma_aluno'))

# --- VER NOTAS (CORREÇÃO DO BUILDERROR) ---
# Adicionamos o parâmetro <int:id_turma> para que o url_for no HTML funcione
@aluno_bp.route("/ver_notas_aluno/<int:id_turma>")
def ver_notas_aluno(id_turma):
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca o nome do exame e a nota que o aluno tirou
    cursor.execute("""
        SELECT e.titulo AS teste, s.pontuacao_total AS nota
        FROM submissoes_exame s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN email em ON a.email_id = em.id
        WHERE em.email_principal = ? AND a.turma_id = ?
        ORDER BY s.data_submissao DESC
    """, (email, id_turma))
    
    notas = cursor.fetchall()
    conn.close()
    
    # Renderiza o template enviando a lista de notas encontrada
    return render_template("ver_notas_aluno.html", notas=notas, id_turma=id_turma)
# --- REALIZAR TESTE (LÓGICA DE POST E GET) ---
@aluno_bp.route("/realizar_teste/<int:id_exame>", methods=["GET", "POST"])
def realizar_teste(id_exame):
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_aluno"))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # 1. Pegar ID do aluno
        cursor.execute("SELECT a.id FROM alunos a JOIN email e ON a.email_id = e.id WHERE e.email_principal = ?", (email,))
        aluno_row = cursor.fetchone()
        aluno_id = aluno_row["id"]

        # 2. Buscar as questões e respostas corretas para este exame
        cursor.execute("""
            SELECT q.id, q.resposta_correta, eq.pontuacao 
            FROM questoes q
            JOIN exame_questoes eq ON q.id = eq.questao_id
            WHERE eq.exame_id = ?
        """, (id_exame,))
        questoes_gabarito = cursor.fetchall()

        pontuacao_total_aluno = 0
        
        # Criar a submissão inicial para obter o ID
        cursor.execute("""
            INSERT INTO submissoes_exame (exame_id, aluno_id, data_submissao, estado)
            VALUES (?, ?, datetime('now'), 'corrigido')
        """, (id_exame, aluno_id))
        submissao_id = cursor.lastrowid

        # 3. Processar respostas e calcular nota
        for q in questoes_gabarito:
            resposta_aluno = request.form.get(f"q{q['id']}")
            pontuacao_atribuida = 0
            
            # Comparação simples (ignora maiúsculas/minúsculas)
            if resposta_aluno and str(resposta_aluno).strip().upper() == str(q['resposta_correta']).strip().upper():
                pontuacao_atribuida = q['pontuacao']
                pontuacao_total_aluno += pontuacao_atribuida

            # Salvar resposta individual
            cursor.execute("""
                INSERT INTO respostas (submissao_id, questao_id, resposta_dada, pontuacao_atribuida)
                VALUES (?, ?, ?, ?)
            """, (submissao_id, q['id'], resposta_aluno, pontuacao_atribuida))

        # 4. Atualizar a nota final na submissão
        cursor.execute("UPDATE submissoes_exame SET pontuacao_total = ? WHERE id = ?", (pontuacao_total_aluno, submissao_id))

        conn.commit()
        conn.close()
        flash(f"Teste enviado! Sua nota foi: {pontuacao_total_aluno}", "success")
        return redirect(url_for("testes_pendentes_aluno_sessao.testes_pendentes_aluno"))

    # GET: Carregar o título do exame e as questões associadas
    # (Mantém igual ao anterior, mas garante que os campos extras da questão venham junto se houver)
    cursor.execute("SELECT titulo FROM exames WHERE id = ?", (id_exame,))
    exame = cursor.fetchone()

    cursor.execute("""
        SELECT q.id, q.enunciado, q.tipo 
        FROM questoes q
        JOIN exame_questoes eq ON q.id = eq.questao_id
        WHERE eq.exame_id = ?
        ORDER BY eq.ordem ASC
    """, (id_exame,))
    questoes = cursor.fetchall()
    conn.close()

    return render_template("realizar_teste.html", exame=exame, questoes=questoes, id_exame=id_exame)