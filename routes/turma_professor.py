from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from willkadasa_db import db_query, db_execute

turma_professor_bp = Blueprint("turma_professor", __name__, url_prefix="/turma_professor")

@turma_professor_bp.route("/<int:id_turma>")
def turma_professor(id_turma):
    email_usuario_logado = session.get('email')
    if not email_usuario_logado:
        return redirect(url_for("login.login_professor"))
    
    # 1. Dados da Turma
    turma = db_query("SELECT * FROM turmas WHERE id = ?", (id_turma,), one=True)
    if not turma:
        return redirect(url_for("professor.dashboard_professor"))
    
    # 2. Alunos
    alunos_na_sala = db_query("SELECT id, email_id, nome, skwd_aluno FROM alunos WHERE turma_id = ?", (id_turma,))
    alunos_disponiveis = db_query("SELECT email_id, nome, skwd_aluno FROM alunos WHERE turma_id IS NULL")
    outras_turmas = db_query("SELECT id, nome FROM turmas WHERE id != ?", (id_turma,))

    # 3. Testes JÁ VINCULADOS a esta turma
    testes_da_turma = db_query("SELECT id, titulo FROM exames WHERE turma_id = ?", (id_turma,))

    # 4. Testes DISPONÍVEIS
# Primeiro, pegamos o ID do professor dono desse e-mail
    prof_data = db_query("""
        SELECT p.id 
        FROM professores p 
        JOIN email e ON p.email_id = e.id 
        WHERE LOWER(e.email_principal) = LOWER(?)
    """, (email_usuario_logado,), one=True)

    testes_disponiveis = []
    if prof_data:
        professor_id = prof_data['id']
        # Agora buscamos os exames usando o ID numérico
        testes_disponiveis = db_query("""
            SELECT e.id, e.titulo, t.nome as nome_turma_atual
            FROM exames e
            LEFT JOIN turmas t ON e.turma_id = t.id
            WHERE e.criado_por = ? 
            AND (e.turma_id IS NULL OR e.turma_id != ?)
        """, (professor_id, id_turma))
    # Lista completa para o modal de "Ver Notas" (histórico geral)
    testes_historico = db_query("""
        SELECT e.id, e.titulo 
        FROM exames e
        JOIN professores p ON e.criado_por = p.id
        JOIN email em ON p.email_id = em.id
        WHERE LOWER(em.email_principal) = LOWER(?)
    """, (email_usuario_logado,))

    return render_template(
        "turma_professor.html", 
        turma=turma, 
        testes_do_professor=testes_historico, # Usado no modal de notas
        testes_disponiveis=testes_disponiveis, # NOVO: Usado para vincular
        testes_da_turma=testes_da_turma,
        alunos=alunos_disponiveis,
        alunos_atualmente_na_sala=alunos_na_sala,
        outras_turmas=outras_turmas
    )

@turma_professor_bp.route("/vincular_alunos/<int:id_turma>", methods=["POST"])
def vincular_alunos(id_turma):
    ids_selecionados = request.form.getlist("alunos")
    if not ids_selecionados:
        flash("Nenhum aluno selecionado.", "warning")
        return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

    try:
        for email_id in ids_selecionados:
            db_execute("UPDATE alunos SET turma_id = ? WHERE email_id = ?", (id_turma, email_id))
        flash(f"{len(ids_selecionados)} aluno(s) vinculados!", "success")
    except Exception as e:
        flash("Erro ao vincular alunos.", "danger")
    
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

# --- ROTA CORRIGIDA PARA VINCULAR TESTE ---
@turma_professor_bp.route("/vincular_teste_existente/<int:id_turma>", methods=["POST"])
def vincular_teste_existente(id_turma):
    id_exame = request.form.get("id_exame")
    if id_exame:
        # Atualiza o teste para pertencer a esta turma
        db_execute("UPDATE exames SET turma_id = ? WHERE id = ?", (id_turma, id_exame))
        flash("Teste vinculado com sucesso!", "success")
    else:
        flash("Erro ao selecionar teste.", "danger")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

# --- ROTA CORRIGIDA PARA DESVINCULAR TESTE ---
# Removemos a complexidade de defaults. Agora exige o ID na URL.
@turma_professor_bp.route("/desvincular_teste/<int:id_turma>", methods=["POST"])
def desvincular_teste(id_turma):
    id_exame = request.form.get("id_exame")
    if id_exame:
        # Define turma_id como NULL apenas para este teste e turma
        db_execute("UPDATE exames SET turma_id = NULL WHERE id = ? AND turma_id = ?", (id_exame, id_turma))
        flash("Teste removido da turma (mas não apagado).", "info")
    else:
        flash("Erro ao identificar o teste.", "danger")
    
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

@turma_professor_bp.route("/transferir_aluno/<int:id_turma_origem>", methods=["POST"])
def transferir_aluno(id_turma_origem):
    email_id = request.form.get("email_id")
    nova_turma_id = request.form.get("nova_turma_id")
    if email_id and nova_turma_id:
        db_execute("UPDATE alunos SET turma_id = ? WHERE email_id = ?", (nova_turma_id, email_id))
        flash("Aluno transferido com sucesso!", "success")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma_origem))

@turma_professor_bp.route("/remover_aluno/<int:id_turma>", methods=["POST"])
def remover_aluno(id_turma):
    email_id = request.form.get("email_id")
    if email_id:
        db_execute("UPDATE alunos SET turma_id = NULL WHERE email_id = ?", (email_id,))
        flash("Aluno removido da turma.", "info")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

@turma_professor_bp.route("/excluir_teste_permanente/<int:id_exame>/<int:id_turma>", methods=["POST"])
def excluir_teste_permanente(id_exame, id_turma):
    try:
        db_execute("DELETE FROM exames WHERE id = ?", (id_exame,))
        flash("Teste excluído permanentemente!", "success")
    except:
        flash("Erro ao excluir. Pode haver notas vinculadas.", "danger")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

# API para notas (mantida igual)
@turma_professor_bp.route("/api/notas_teste/<int:id_exame>/<int:id_turma>")
def api_notas_teste(id_exame, id_turma):
    notas = db_query("""
        SELECT a.nome, COALESCE(r.nota, 0) as nota
        FROM alunos a
        LEFT JOIN resultados r ON a.id = r.aluno_id AND r.exame_id = ?
        WHERE a.turma_id = ?
    """, (id_exame, id_turma))
    
    dados = [{"nome": row["nome"], "nota": row["nota"]} for row in notas]
    return jsonify(dados)