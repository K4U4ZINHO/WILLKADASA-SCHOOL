from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# Importamos as funções do seu banco de dados híbrido
from willkadasa_db import db_query, db_execute

turma_professor_bp = Blueprint("turma_professor", __name__, url_prefix="/turma_professor")

# --- VER TURMA E GERENCIAR ---
@turma_professor_bp.route("/<int:id_turma>")
def turma_professor(id_turma):
    email_usuario_logado = session.get('email')
    if not email_usuario_logado:
        return redirect(url_for("login.login_professor"))
    
    # 1. Dados da Turma
    turma = db_query("SELECT * FROM turmas WHERE id = ?", (id_turma,), one=True)
    
    # 2. Alunos que JÁ ESTÃO nesta turma
    alunos_na_sala = db_query("SELECT id, email_id, nome, skwd_aluno FROM alunos WHERE turma_id = ?", (id_turma,))
    
    # 3. Alunos SEM TURMA (para o dropdown de vincular)
    alunos_disponiveis = db_query("SELECT email_id, nome, skwd_aluno FROM alunos WHERE turma_id IS NULL")

    # 4. Outras turmas (para transferência)
    outras_turmas = db_query("SELECT id, nome FROM turmas WHERE id != ?", (id_turma,))

    # 5. Testes do professor que podem ser vinculados
    testes_do_professor = db_query("""
        SELECT e.id, e.titulo 
        FROM exames e
        JOIN professores p ON e.criado_por = p.id
        JOIN email em ON p.email_id = em.id
        WHERE LOWER(em.email_principal) = LOWER(?)
    """, (email_usuario_logado,))
    
    # 6. Testes JÁ VINCULADOS a esta turma
    testes_da_turma = db_query("SELECT id, titulo FROM exames WHERE turma_id = ?", (id_turma,))

    return render_template(
        "turma_professor.html", 
        turma=turma, 
        testes_do_professor=testes_do_professor, 
        testes_da_turma=testes_da_turma, # Adicionado para listar testes ativos na sala
        alunos=alunos_disponiveis,
        alunos_atualmente_na_sala=alunos_na_sala,
        outras_turmas=outras_turmas
    )

# --- VINCULAR ALUNOS ---
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
        flash(f"Erro ao vincular: {e}", "danger")
        
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

# --- VINCULAR TESTE ---
@turma_professor_bp.route("/vincular_teste_existente/<int:id_turma>", methods=["POST"])
def vincular_teste_existente(id_turma):
    id_exame = request.form.get("id_exame")
    if not id_exame:
        flash("Erro: Teste não identificado.", "danger")
        return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

    db_execute("UPDATE exames SET turma_id = ? WHERE id = ?", (id_turma, id_exame))
    flash("Teste vinculado com sucesso!", "success")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

# --- REMOVER/TRANSFERIR ALUNOS ---
@turma_professor_bp.route("/remover_aluno/<int:id_turma>", methods=["POST"])
def remover_aluno(id_turma):
    email_id = request.form.get("email_id")
    db_execute("UPDATE alunos SET turma_id = NULL WHERE email_id = ?", (email_id,))
    flash("Aluno removido da turma.", "info")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

@turma_professor_bp.route("/transferir_aluno/<int:id_turma_origem>", methods=["POST"])
def transferir_aluno(id_turma_origem):
    email_id = request.form.get("email_id")
    nova_turma_id = request.form.get("nova_turma_id")
    db_execute("UPDATE alunos SET turma_id = ? WHERE email_id = ?", (nova_turma_id, email_id))
    flash("Aluno transferido com sucesso!", "success")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma_origem))

# --- DESVINCULAR TESTE ---
@turma_professor_bp.route("/desvincular_teste/<int:id_turma>", methods=["POST"])
def desvincular_teste(id_turma):
    id_exame = request.form.get("id_exame")
    db_execute("UPDATE exames SET turma_id = NULL WHERE id = ? AND turma_id = ?", (id_exame, id_turma))
    flash("Teste desvinculado desta turma!", "success")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))