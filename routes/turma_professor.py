from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3

turma_professor_bp = Blueprint("turma_professor", __name__, url_prefix="/turma_professor")

def get_db_connection():
    conn = sqlite3.connect("willkadasa.db")
    conn.row_factory = sqlite3.Row
    return conn

@turma_professor_bp.route("/<int:id_turma>")
def turma_professor(id_turma):
    email_usuario_logado = session.get('email')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Dados da Turma
    cursor.execute("SELECT * FROM turmas WHERE id = ?", (id_turma,))
    turma = cursor.fetchone()
    
    # 2. Alunos que JÁ ESTÃO nesta turma (Para remover/transferir)
    cursor.execute("SELECT id, email_id, nome, skwd_aluno FROM alunos WHERE turma_id = ?", (id_turma,))
    alunos_na_sala = cursor.fetchall()
    
    # 3. Alunos SEM TURMA (Para o modal de vincular novos)
    cursor.execute("SELECT email_id, nome, skwd_aluno FROM alunos WHERE turma_id IS NULL")
    alunos_disponiveis = cursor.fetchall()

    # 4. Todas as turmas (Para o menu de transferência)
    cursor.execute("SELECT id, nome FROM turmas WHERE id != ?", (id_turma,))
    outras_turmas = cursor.fetchall()

    # 5. Testes do professor
    cursor.execute("""
        SELECT e.id, e.titulo 
        FROM exames e
        JOIN professores p ON e.criado_por = p.id
        JOIN email em ON p.email_id = em.id
        WHERE LOWER(em.email_principal) = LOWER(?)
    """, (email_usuario_logado,))
    testes_do_professor = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        "turma_professor.html", 
        turma=turma, 
        testes_do_professor=testes_do_professor, 
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
    id_exame = request.form.get("id_exame")
    
    if not id_exame:
        flash("Erro: Teste não identificado.", "danger")
        return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # AGORA SIM: Gravamos qual turma pode ver este teste
        cursor.execute("""
            UPDATE exames 
            SET turma_id = ? 
            WHERE id = ?
        """, (id_turma, id_exame))
        
        conn.commit()
        flash("Teste vinculado à turma com sucesso! Os alunos já podem visualizar.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao vincular: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

@turma_professor_bp.route("/notas_individuais/<int:id_turma>")
def notas_individuais(id_turma):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Busca apenas os alunos que já pertencem a ESTA turma
    cursor.execute("SELECT id, nome FROM alunos WHERE turma_id = ?", (id_turma,))
    alunos_da_turma = cursor.fetchall()
    
    # 2. Busca as notas de cada aluno
    notas_por_aluno = {}
    for aluno in alunos_da_turma:
        cursor.execute("""
            SELECT e.titulo, s.pontuacao_total 
            FROM submissoes_exame s
            JOIN exames e ON s.exame_id = e.id
            WHERE s.aluno_id = ?
        """, (aluno['id'],))
        notas_por_aluno[aluno['id']] = cursor.fetchall()

    conn.close()
    return render_template("notas_individuais.html", 
                        alunos=alunos_da_turma, 
                        notas_por_aluno=notas_por_aluno,
                        id_turma=id_turma)

@turma_professor_bp.route("/notas_por_teste/<int:id_turma>")
def notas_por_teste(id_turma):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Busca todos os testes vinculados a esta turma
    # (Certifique-se que a tabela exames tem a coluna turma_id)
    cursor.execute("""
        SELECT id, titulo, data_hora_inicio 
        FROM exames 
        WHERE turma_id = ?
    """, (id_turma,))
    testes = cursor.fetchall()
    
    # 2. Para cada teste, busca as notas dos alunos que submeteram
    resultados_por_teste = {}
    for teste in testes:
        cursor.execute("""
            SELECT a.nome, s.pontuacao_total, s.data_submissao
            FROM submissoes_exame s
            JOIN alunos a ON s.aluno_id = a.id
            WHERE s.exame_id = ?
            ORDER BY s.pontuacao_total DESC
        """, (teste['id'],))
        resultados_por_teste[teste['id']] = cursor.fetchall()

    conn.close()
    return render_template("notas_por_teste.html", 
                        testes=testes, 
                        resultados=resultados_por_teste, 
                        id_turma=id_turma)

@turma_professor_bp.route("/ver_notas_teste/<int:id_exame>/<int:id_turma>")
def ver_notas_teste(id_exame, id_turma):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Busca informações do Exame para o cabeçalho
    cursor.execute("SELECT titulo FROM exames WHERE id = ?", (id_exame,))
    exame = cursor.fetchone()
    
    # 2. Busca informações da Turma
    cursor.execute("SELECT nome FROM turmas WHERE id = ?", (id_turma,))
    turma = cursor.fetchone()

    # 3. Busca a lista de alunos da turma e suas respectivas notas para este exame
    # Usamos LEFT JOIN para mostrar o aluno mesmo que ele ainda não tenha feito o teste
    cursor.execute("""
        SELECT 
            a.nome as nome_aluno,
            s.pontuacao_total,
            s.data_submissao
        FROM alunos a
        LEFT JOIN submissoes_exame s ON a.id = s.aluno_id AND s.exame_id = ?
        WHERE a.turma_id = ?
        ORDER BY a.nome ASC
    """, (id_exame, id_turma))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return render_template(
        "detalhe_notas_teste.html", 
        exame=exame, 
        turma=turma, 
        resultados=resultados,
        id_turma=id_turma
    )

@turma_professor_bp.route("/api/notas_teste/<int:id_exame>/<int:id_turma>")
def api_notas_teste(id_exame, id_turma):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca alunos da turma e suas notas para este exame específico
    cursor.execute("""
        SELECT a.nome, s.pontuacao_total
        FROM alunos a
        LEFT JOIN submissoes_exame s ON a.id = s.aluno_id AND s.exame_id = ?
        WHERE a.turma_id = ?
    """, (id_exame, id_turma))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return jsonify([{"nome": r["nome"], "nota": r["pontuacao_total"] if r["pontuacao_total"] is not None else "---"} for r in resultados])

@turma_professor_bp.route("/desvincular_teste/<int:id_turma>", methods=["POST"])
def desvincular_teste(id_turma):
    id_exame = request.form.get("id_exame")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Já que não há coluna turma_id em exames, 
        # vamos remover as submissões deste exame feitas pelos alunos desta turma.
        # Isso faz com que o teste pare de aparecer nos resultados da turma.
        cursor.execute("""
            DELETE FROM submissoes_exame 
            WHERE exame_id = ? AND aluno_id IN (SELECT id FROM alunos WHERE turma_id = ?)
        """, (id_exame, id_turma))
        
        conn.commit()
        flash("Vínculos e notas do teste removidos desta turma!", "success")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao excluir: {e}")
        flash(f"Erro ao excluir teste: {e}", "danger")
    finally:
        conn.close()
    
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

@turma_professor_bp.route("/excluir_teste_permanente/<int:id_exame>/<int:id_turma>", methods=["POST"])
def excluir_teste_permanente(id_exame, id_turma):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ativamos as chaves estrangeiras para garantir que o CASCADE funcione
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Deleta o exame permanentemente do banco
        cursor.execute("DELETE FROM exames WHERE id = ?", (id_exame,))
        
        conn.commit()
        flash("Teste excluído permanentemente do sistema!", "success")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao deletar: {e}")
        flash("Erro ao excluir o teste do banco de dados.", "danger")
    finally:
        conn.close()
    
    # Redireciona de volta para a página da turma
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))
# Verifique se o nome da função é exatamente 'remover_aluno'
@turma_professor_bp.route("/remover_aluno/<int:id_turma>", methods=["POST"])
def remover_aluno(id_turma):
    email_id = request.form.get("email_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE alunos SET turma_id = NULL WHERE email_id = ?", (email_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma))

# Verifique se o nome da função é exatamente 'transferir_aluno'
@turma_professor_bp.route("/transferir_aluno/<int:id_turma_origem>", methods=["POST"])
def transferir_aluno(id_turma_origem):
    email_id = request.form.get("email_id")
    nova_turma_id = request.form.get("nova_turma_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE alunos SET turma_id = ? WHERE email_id = ?", (nova_turma_id, email_id))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("turma_professor.turma_professor", id_turma=id_turma_origem))
