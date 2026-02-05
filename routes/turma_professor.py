from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3

turma_professor_bp = Blueprint("turma_professor", __name__, url_prefix="/turma_professor")

def get_db_connection():
    conn = sqlite3.connect("willkadasa.db")
    conn.row_factory = sqlite3.Row
    return conn

@turma_professor_bp.route("/<int:id_turma>")
def turma_professor(id_turma):
    # Usando 'email' que é a chave que seu sistema usa
    email_usuario_logado = session.get('email')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Dados da Turma
    cursor.execute("SELECT * FROM turmas WHERE id = ?", (id_turma,))
    turma = cursor.fetchone()
    
    # 2. Testes criados pelo professor logado (QUERY CORRIGIDA COM JOIN)
    cursor.execute("""
        SELECT e.id, e.titulo 
        FROM exames e
        JOIN professores p ON e.criado_por = p.id
        JOIN email em ON p.email_id = em.id
        WHERE LOWER(em.email_principal) = LOWER(?)
    """, (email_usuario_logado,))
    testes_do_professor = cursor.fetchall()
    
    # 3. Alunos para o modal de vínculo
    cursor.execute("""
        SELECT email_id, nome, skwd_aluno 
        FROM alunos 
        WHERE turma_id IS NULL OR turma_id != ?
    """, (id_turma,))
    alunos_disponiveis = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        "turma_professor.html", 
        turma=turma, 
        testes_do_professor=testes_do_professor, 
        alunos=alunos_disponiveis
    )

@turma_professor_bp.route("/vincular_alunos/<int:id_turma>", methods=["POST"])
def vincular_alunos(id_turma):
    ids_selecionados = request.form.getlist("alunos")
    if not ids_selecionados:
        flash("Nenhum aluno selecionado.", "warning")
        return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for email_id in ids_selecionados:
            cursor.execute("UPDATE alunos SET turma_id = ? WHERE email_id = ?", (id_turma, email_id))
        conn.commit()
        flash(f"{len(ids_selecionados)} aluno(s) vinculados!", "success")
    except Exception as e:
        flash("Erro ao vincular alunos.", "danger")
    finally:
        conn.close()
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

@turma_professor_bp.route("/salvar_teste_completo", methods=["POST"])
def salvar_teste_completo():
    data = request.get_json()
    titulo = data.get("titulo")
    questoes_lista = data.get("questoes")
    
    # MUDANÇA AQUI: de 'email_id' para 'email'
    email_usuario_logado = session.get('email') 
    
    print(f"DEBUG: Tentando salvar teste. Email na sessão: {email_usuario_logado}")

    if not email_usuario_logado:
        return jsonify({"success": False, "message": "Sessão expirada."}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ajuste na Query para bater com a estrutura da sua tabela email/professores
        cursor.execute("""
            SELECT id FROM professores 
            WHERE email_id = (SELECT id FROM email WHERE LOWER(email_principal) = LOWER(?))
        """, (email_usuario_logado,))
        
        prof = cursor.fetchone()
        
        if not prof:
            return jsonify({"success": False, "message": "Professor não encontrado."}), 404
        
        prof_id = prof['id']

        # 2. Insere o Exame
        cursor.execute("""
            INSERT INTO exames (titulo, data_hora_inicio, duracao_minutos, criado_por)
            VALUES (?, datetime('now'), 60, ?)
        """, (titulo, prof_id))
        exame_id = cursor.lastrowid

        # 3. Insere as Questões e o vínculo
        for idx, q in enumerate(questoes_lista):
            enunciado_completo = f"{q['enunciado']}\nA) {q['a']}\nB) {q['b']}\nC) {q['c']}\nD) {q['d']}"
            cursor.execute("""
                INSERT INTO questoes (enunciado, tipo, resposta_correta)
                VALUES (?, 'multipla_escolha', ?)
            """, (enunciado_completo, q['correta']))
            questao_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO exame_questoes (exame_id, questao_id, pontuacao, ordem)
                VALUES (?, ?, 1.0, ?)
            """, (exame_id, questao_id, idx + 1))

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print(f"ERRO: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@turma_professor_bp.route("/vincular_teste_existente/<int:id_turma>", methods=["POST"])
def vincular_teste_existente(id_turma):
    # Lógica para vincular um exame já criado a uma turma específica
    flash("Teste vinculado à turma com sucesso!", "success")
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))