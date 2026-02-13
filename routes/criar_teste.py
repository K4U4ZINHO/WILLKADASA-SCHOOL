from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime
from willkadasa_db import db_query, get_db
import sqlite3

criar_teste_bp = Blueprint("criar_teste", __name__, url_prefix="/professor")

# ROTA 1: EXIBE O FORMULÁRIO (HTML)
@criar_teste_bp.route("/criar_teste", methods=["GET"])
def criar_teste():
    email = session.get("email")
    if not email:
        return redirect(url_for("login.login_professor"))

    id_turma = request.args.get("id_turma")

    resultado = db_query("""
        SELECT e.nome, p.disciplinas, p.id as professor_id
        FROM professores p
        JOIN email e ON p.email_id = e.id
        WHERE LOWER(e.email_principal) = LOWER(?)
    """, (email,), one=True)

    if not resultado:
        nome_professor = "Professor"
        disciplinas = ""
    else:
        nome_professor = resultado["nome"]
        disciplinas = resultado["disciplinas"]

    lista_disciplinas = [d.strip() for d in disciplinas.split(",")] if disciplinas else []
    
    mes = datetime.now().month
    trimestres = {1: "1º Trimestre", 2: "1º Trimestre", 3: "1º Trimestre", 
                  4: "2º Trimestre", 5: "2º Trimestre", 6: "2º Trimestre",
                  7: "3º Trimestre", 8: "3º Trimestre", 9: "3º Trimestre"}
    trimestre = trimestres.get(mes, "4º Trimestre")
    titulo_sugerido = f"Avaliação {trimestre}"

    return render_template(
        "criar_teste.html",
        nome_professor=nome_professor,
        disciplinas=lista_disciplinas,
        titulo_sugerido=titulo_sugerido,
        id_turma=id_turma
    )

# ROTA 2: PROCESSA O SALVAMENTO (JSON)
@criar_teste_bp.route("/salvar_teste_no_db", methods=["GET", "POST"])
def salvar_teste_no_db():
    if request.method == "GET":
        return redirect(url_for("criar_teste.criar_teste"))
    
    try:
        dados = request.get_json()
        email_logado = session.get("email")
        
        if not email_logado:
            return jsonify({"success": False, "message": "Sessão expirada."}), 401

        prof = db_query("""
            SELECT p.id FROM professores p 
            JOIN email e ON p.email_id = e.id 
            WHERE LOWER(e.email_principal) = LOWER(?)
        """, (email_logado,), one=True)
        
        if not prof:
            return jsonify({"success": False, "message": "Professor não encontrado."}), 404
        
        professor_id = prof['id']
        titulo = dados.get('titulo')
        questoes_lista = dados.get('questoes')
        id_turma = dados.get('id_turma')
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = get_db()
        cur = conn.cursor()

        # 1. Inserir o Exame
        sql_exame = """
            INSERT INTO exames (titulo, data_hora_inicio, duracao_minutos, criado_por, turma_id)
            VALUES (?, ?, ?, ?, ?)
        """
        params_exame = (titulo, data_atual, 60, professor_id, id_turma)

        if isinstance(conn, sqlite3.Connection):
            cur.execute(sql_exame, params_exame)
            exame_id = cur.lastrowid
        else:
            cur.execute(sql_exame.replace("?", "%s") + " RETURNING id", params_exame)
            exame_id = cur.fetchone()[0]

        # 2. Inserir cada Questão e vincular ao Exame
        for i, q in enumerate(questoes_lista):
            enunciado = q.get('enunciado')
            res_correta = q.get('correta')
            op_a = q.get('a')
            op_b = q.get('b')
            op_c = q.get('c')
            op_d = q.get('d')

            sql_q = """
                INSERT INTO questoes (enunciado, tipo, resposta_correta, opcao_a, opcao_b, opcao_c, opcao_d) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params_q = (enunciado, "multipla_escolha", res_correta, op_a, op_b, op_c, op_d)

            if isinstance(conn, sqlite3.Connection):
                cur.execute(sql_q, params_q)
                q_id = cur.lastrowid
            else:
                cur.execute(sql_q.replace("?", "%s") + " RETURNING id", params_q)
                q_id = cur.fetchone()[0]

            # Vincula a questão ao exame
            sql_vinculo = "INSERT INTO exame_questoes (exame_id, questao_id, pontuacao, ordem) VALUES (?, ?, ?, ?)"
            cur.execute(sql_vinculo.replace("?", "%s") if not isinstance(conn, sqlite3.Connection) else sql_vinculo, 
                        (exame_id, q_id, 1.0, i + 1))

        # 3. Finaliza a transação
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "message": "Teste salvo com sucesso!"})

    except Exception as e:
        print(f"Erro ao salvar teste: {e}")
        return jsonify({"success": False, "message": "Erro ao salvar: " + str(e)}), 500