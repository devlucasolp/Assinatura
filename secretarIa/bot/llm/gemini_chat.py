"""
BOT - Módulo de chat com contexto completo (histórico Postgres + cache Redis)
Usa Gemini para o chat principal e classificação de intenção.
"""

import json
from core.logger import bot_logger
from integrations.postgres import get_conversation_history, save_conversation_message
import google.generativeai as genai
from core.context import get_current_instance

# ---------------------------------------------------------------------------
# Asana Tools for Gemini
# ---------------------------------------------------------------------------

async def list_my_tasks(status: str = "todas") -> str:
    """
    Retorna as tarefas incompletas atribuídas à Gabriela no Asana filtradas por status.
    Use esta função sempre que o usuário perguntar o que tem para fazer, tarefas atrasadas, tarefas de hoje, amanhã ou resumo do Asana.
    
    Args:
        status: O status das tarefas a buscar. Valores permitidos:
                'atrasadas' (vencidas antes de hoje),
                'hoje' (vencendo hoje),
                'amanha' (vencendo amanhã),
                'em_dia' (vencendo nos próximos 7 dias, exceto as atrasadas),
                'todas' (todas as tarefas incompletas).
    """
    from integrations.asana_client import get_my_tasks
    try:
        if status == "atrasadas":
            tasks = await get_my_tasks(overdue_only=True)
        elif status == "hoje":
            tasks = await get_my_tasks(days_ahead=0)
        elif status == "amanha":
            from datetime import date, timedelta
            all_tasks = await get_my_tasks(days_ahead=1)
            tomorrow_str = (date.today() + timedelta(days=1)).isoformat()
            tasks = [t for t in all_tasks if t.get("due_on") == tomorrow_str]
        elif status == "em_dia":
            tasks = await get_my_tasks(days_ahead=7)
        else:
            tasks = await get_my_tasks()
        
        if not tasks:
            return f"Nenhuma tarefa encontrada com status '{status}' no Asana."
            
        lines = []
        for t in tasks:
            due = t.get("due_on")
            due_str = f" (vence: {due})" if due else " (sem prazo)"
            completed = " [Concluída]" if t.get("completed") else ""
            lines.append(f"- {t['name']}{due_str}{completed}\n  GID: {t['gid']}\n  Link: {t.get('permalink_url', 'Sem link')}")
        return "\n".join(lines)
    except Exception as e:
        return f"Erro ao listar tarefas do Asana: {str(e)}"


async def search_tasks_by_name(query: str) -> str:
    """
    Busca tarefas no Asana pelo nome para obter o GID e o link.
    Útil antes de atualizar, concluir, deletar ou comentar em uma tarefa pelo nome.
    
    Args:
        query: O termo de busca ou nome da tarefa (ex: 'reuniao bplast').
    """
    from integrations.asana_client import search_task_by_name
    try:
        results = await search_task_by_name(query)
        if not results:
            return f"Nenhuma tarefa encontrada no Asana com o termo '{query}'."
        
        lines = []
        for t in results:
            lines.append(f"- {t['name']}\n  GID: {t['gid']}\n  Link: {t.get('permalink_url', 'Sem link')}")
        return "\n".join(lines)
    except Exception as e:
        return f"Erro ao buscar tarefas por nome: {str(e)}"


async def add_comment_to_task_tool(task_gid: str, comment_text: str) -> str:
    """
    Adiciona um comentário a uma tarefa específica no Asana pelo GID.
    
    Args:
        task_gid: O GID (identificador único) da tarefa no Asana.
        comment_text: O texto do comentário a ser adicionado (ex: 'oi').
    """
    from integrations.asana_client import add_comment_to_task
    try:
        await add_comment_to_task(task_gid, comment_text)
        return f"Comentário '{comment_text}' adicionado com sucesso à tarefa {task_gid}."
    except Exception as e:
        return f"Erro ao adicionar comentário: {str(e)}"


async def complete_task_in_asana(task_gid: str) -> str:
    """
    Marca uma tarefa no Asana como concluída pelo GID.
    
    Args:
        task_gid: O GID da tarefa no Asana.
    """
    from integrations.asana_client import complete_task
    try:
        await complete_task(task_gid)
        return f"Tarefa {task_gid} concluída com sucesso."
    except Exception as e:
        return f"Erro ao concluir tarefa: {str(e)}"


async def update_task_fields(
    task_gid: str,
    name: str | None = None,
    due_on: str | None = None,
    notes: str | None = None,
) -> str:
    """
    Atualiza um ou mais campos de uma tarefa no Asana.
    
    Args:
        task_gid: O GID da tarefa no Asana.
        name: Novo nome para a tarefa (opcional).
        due_on: Nova data de vencimento no formato YYYY-MM-DD (opcional).
        notes: Novas notas ou descrição da tarefa (opcional).
    """
    from integrations.asana_client import update_task
    try:
        fields = {}
        if name:
            fields["name"] = name
        if due_on:
            fields["due_on"] = due_on
        if notes:
            fields["notes"] = notes
            
        if not fields:
            return "Nenhum campo fornecido para atualização."
            
        await update_task(task_gid, fields)
        return f"Tarefa {task_gid} atualizada com sucesso. Campos alterados: {list(fields.keys())}"
    except Exception as e:
        return f"Erro ao atualizar tarefa: {str(e)}"


async def delete_task_from_asana(task_gid: str) -> str:
    """
    Exclui uma tarefa no Asana pelo GID.

    Args:
        task_gid: O GID da tarefa no Asana.
    """
    from integrations.asana_client import delete_task
    try:
        await delete_task(task_gid)
        return f"Tarefa {task_gid} deletada com sucesso."
    except Exception as e:
        return f"Erro ao deletar tarefa: {str(e)}"


async def python_exec(code: str) -> str:
    """
    Executa código Python em sandbox isolada para fazer cálculos, análises de dados,
    manipulação de strings/datas, geração de gráficos ou qualquer computação ad-hoc.

    Bibliotecas disponíveis: numpy, pandas, matplotlib, scipy, httpx, requests, datetime, json, re.

    Use quando o pedido envolver:
    - Cálculos não-triviais (médias, projeções, estatísticas, conversões)
    - Análise de dados em formato tabular
    - Manipulação de datas e cronogramas
    - Qualquer tarefa onde código resolve melhor que texto.

    NÃO use para:
    - Operações no Asana (use as ferramentas dedicadas)
    - Conversa simples (responda direto)

    Args:
        code: Código Python completo que imprime o resultado via print().
              A última linha deve produzir o output via print() — return não funciona.
              Exemplo: "import pandas as pd\\ndf = pd.DataFrame({'a':[1,2,3]})\\nprint(df.sum())"
    """
    from integrations.sandbox import execute_python
    instance = get_current_instance()
    try:
        result = await execute_python(
            code=code,
            instance_id=instance.get("id", "default"),
            origin="gemini",
        )
        return result.to_llm_message()
    except Exception as e:
        return f"Erro ao executar código: {str(e)}"


async def toggle_briefings(morning: str | None = None, afternoon: str | None = None, evening: str | None = None) -> str:
    """
    Liga, desliga ou altera os horários dos briefings diários do Asana.
    Args:
        morning: Horário no formato HH:MM (ex: '07:00') ou string vazia '' para desativar. Use None para manter o atual.
        afternoon: Horário no formato HH:MM ou string vazia para desativar. Use None para manter o atual.
        evening: Horário no formato HH:MM ou string vazia para desativar. Use None para manter o atual.
    """
    from integrations.postgres import get_pool
    instance = get_current_instance()
    instance_id = instance.get("id")
    updates = []
    values = []
    if morning is not None:
        values.append(morning if morning else None)
        updates.append(f"briefing_morning = ${len(values)}")
    if afternoon is not None:
        values.append(afternoon if afternoon else None)
        updates.append(f"briefing_afternoon = ${len(values)}")
    if evening is not None:
        values.append(evening if evening else None)
        updates.append(f"briefing_evening = ${len(values)}")
    if not updates:
        return "Nenhuma alteração enviada."
    values.append(instance_id)
    query = f"UPDATE bots.instances SET {', '.join(updates)} WHERE id = ${len(values)}"
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(query, *values)
    return "Horários dos briefings atualizados com sucesso."

async def create_scheduled_task(name: str, cron_expression: str, code: str) -> str:
    """
    Cria ou atualiza uma tarefa agendada que roda código Python na Sandbox periodicamente.
    Args:
        name: Nome descritivo da tarefa.
        cron_expression: Expressão CRON de 5 campos (ex: '0 7 * * *' para todo dia às 7h).
        code: Código Python que será executado no Sandbox. Use requests para /api/internal/send_message se precisar enviar msg.
    """
    from integrations.postgres import get_pool
    instance = get_current_instance()
    instance_id = instance.get("id")
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            '''
            INSERT INTO bots.scheduled_tasks (instance_id, name, cron_expression, code, enabled, created_at, updated_at)
            VALUES ($1, $2, $3, $4, TRUE, NOW(), NOW())
            ''',
            instance_id, name, cron_expression, code
        )
    return f"Tarefa '{name}' agendada com sucesso! (CRON: {cron_expression})"

async def create_webhook(slug: str, code: str) -> str:
    """
    Cria um Webhook para receber requisições de outros sistemas.
    Args:
        slug: O nome da rota URL (apenas letras, números e hífens). Ex: 'github-events'
        code: Código Python executado ao receber o webhook. O body está em WEBHOOK_PAYLOAD.
    """
    from integrations.postgres import get_pool
    instance = get_current_instance()
    instance_id = instance.get("id")
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            '''
            INSERT INTO bots.webhooks (instance_id, slug, code, enabled, created_at, updated_at)
            VALUES ($1, $2, $3, TRUE, NOW(), NOW())
            ON CONFLICT (instance_id, slug) DO UPDATE SET code = $3, enabled = TRUE, updated_at = NOW()
            ''',
            instance_id, slug, code
        )
    import os
    base_url = os.getenv("BOT_PUBLIC_URL", "http://localhost:8000")
    return f"Webhook '{slug}' criado! URL: {base_url}/api/webhooks/{instance_id}/{slug}"


def _get_model_with_tools():
    instance = get_current_instance()
    api_key = instance.get("gemini_api_key", "")
    if not api_key:
        from core.config import get_settings
        api_key = get_settings().gemini.api_key
    if not api_key:
        return None
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        "gemini-2.5-flash",
        tools=[
            list_my_tasks,
            search_tasks_by_name,
            add_comment_to_task_tool,
            complete_task_in_asana,
            update_task_fields,
            delete_task_from_asana,
            python_exec,
            toggle_briefings,
            create_scheduled_task,
            create_webhook,
        ]
    )

def _get_base_model():
    instance = get_current_instance()
    api_key = instance.get("gemini_api_key", "")
    if not api_key:
        from core.config import get_settings
        api_key = get_settings().gemini.api_key
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT_GABI = """Você é a Fernanda, secretária executiva particular da Gabriela. Trabalha com ela há anos e conhece seu jeito, suas prioridades e o ritmo da Assinatura.

## Personalidade e comunicação

- Fala como uma profissional experiente: direta, discreta, sem rodeios, sem robotismo.
- Entende linguagem informal, abreviações, jargões do dia a dia ("faz esse negócio lá", "aquela reunião de ontem", "o projeto da Marcelle"). Use contexto para interpretar.
- Quando a instrução for vaga, interpreta pelo melhor resultado possível — só pergunta o que for estritamente necessário para executar. Máximo uma pergunta por vez.
- Jamais faz sermão, não explica o óbvio, não repete o que a Gabriela acabou de dizer.
- Tom: próximo, profissional, sem bajulação. Resposta curta quando o assunto é simples; mais detalhada só quando o assunto pede.

## O que você FAZ neste chat

- Apoio executivo geral: rascunhos de e-mail, resumos, textos, organização de informações, perguntas do dia a dia.
- Interpretar pedidos e coletar as informações necessárias para executá-los.

## Ações no Asana (IMPORTANTE — leia com atenção)

- Criação de novas tarefas, reuniões e atas no Asana ainda são executadas por um sistema separado de roteamento de intenção. Se a Gabriela pedir para CRIAR uma tarefa ou reunião nova, você apenas reconhece e diz que está processando (o sistema de roteamento fará o resto).
- Para todas as OUTRAS ações em tarefas existentes (como ver o que está atrasado, ver o que tem hoje/amanhã, buscar tarefas, concluir tarefas, alterar data/nome/notas de tarefas ou adicionar comentários/comentar), você possui FERRAMENTAS nativas.
- Sempre use as ferramentas adequadas para buscar, listar ou alterar as tarefas no Asana em tempo real quando solicitado de forma fluida.
- Se a Gabriela pedir para listar tarefas atrasadas ou tarefas do Asana, use a ferramenta `list_my_tasks`.
- Se ela pedir para comentar em uma tarefa (ex: "comente 'oi' na minha task reuniao bplast"), primeiro busque a tarefa pelo nome com `search_tasks_by_name` para obter o GID correto, e depois chame a ferramenta `add_comment_to_task_tool` com o GID e o texto do comentário.
- Se ela pedir para marcar como concluída, atualizar ou deletar, faça o mesmo: busque pelo nome para obter o GID e depois chame a ferramenta correspondente.
- Forneça os links reais das tarefas (permalink_url) retornados pelas ferramentas nas suas respostas.
- NUNCA invente GIDs ou links do Asana.

## Cálculos e análises (ferramenta `python_exec`)

- Para qualquer cálculo não-trivial (médias, projeções, contagens com filtros, conversões de unidades, análise de datas, estatísticas), use a ferramenta `python_exec` em vez de calcular mentalmente.
- O código deve imprimir o resultado via `print()`. Bibliotecas disponíveis: numpy, pandas, matplotlib, scipy, httpx, requests, datetime.
- Para perguntas simples ("quanto é 2+2"), responda direto sem usar a ferramenta.

## Regras inegociáveis

- Os comandos da Gabriela são lei. Se ela mandar fazer de um jeito específico, faça exatamente assim.
- Não use emojis excessivos. No máximo um, quando fizer sentido.
- Não termine com "Se precisar de mais alguma coisa...". Só responda o que foi pedido.
- Sempre responda em português brasileiro.
"""

_INTENT_PROMPT = """Você é um classificador de intenção para uma assistente executiva via WhatsApp.

Analise a mensagem do usuário (e o histórico de contexto, se houver) e retorne SOMENTE um JSON válido com a chave "intent" e um destes valores:

- "asana_task"     — usuário quer CRIAR uma tarefa, reunião, agendamento ou evento no Asana
                     (incluindo "tente novamente", "faz de novo" quando contexto indica criação anterior)
- "asana_query"    — usuário quer CONSULTAR/LER tarefas do Asana
                     ("o que tenho hoje?", "minhas tarefas", "tem algo atrasado?", "resumo", "pendências")
- "asana_update"   — usuário quer ALTERAR uma tarefa existente
                     (mudar nome, data, notas — ex: "muda o prazo da tarefa X", "renomeia a tarefa Y")
- "asana_delete"   — usuário quer DELETAR/REMOVER uma tarefa existente
                     ("deleta a tarefa X", "remove a reunião Y", "apaga a tarefa")
- "asana_complete" — usuário quer MARCAR tarefa como CONCLUÍDA/FEITA
                     ("conclui a tarefa X", "marca como feita", "finalizei a reunião Y")
- "asana_search"   — usuário quer BUSCAR uma tarefa específica pelo nome ou pegar o link dela
                     ("qual o link da tarefa X", "busca a tarefa Y", "me manda o link da reunião Z")
- "link_request"   — usuário pede o link da ÚLTIMA tarefa criada, sem especificar nome
                     ("quero o link", "me manda o link", "me passa o link")
- "ata"            — usuário quer processar uma ata de reunião a partir de transcrição/notas
- "chat"           — qualquer outra coisa (conversa, dúvida, pedido de rascunho, etc.)

Responda apenas com o JSON. Exemplo: {"intent": "asana_task"}
"""


async def classify_intent(text: str, history: list[dict]) -> str:
    """
    Classifica a intenção da mensagem usando Gemini como roteamento.
    Retorna: "asana_task" | "link_request" | "ata" | "chat"
    """
    model = _get_base_model()
    if not model:
        return "chat"

    # Últimas 3 trocas de histórico para contexto
    recent = history[-6:] if len(history) > 6 else history
    
    # Formata o histórico para o prompt
    history_text = ""
    if recent:
        history_text = "Histórico recente:\n"
        for msg in recent:
            role = "Usuário" if msg["role"] == "user" else "Assistente"
            history_text += f"{role}: {msg['content']}\n"
    
    prompt = f"{_INTENT_PROMPT}\n\n{history_text}\nMensagem atual do usuário: {text}"

    try:
        response = await model.generate_content_async(prompt)
        raw = response.text.strip()

        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        result = json.loads(raw)
        intent = result.get("intent", "chat")
        bot_logger.debug(f"[BOT] Intent classificado: '{intent}' para: {text[:60]!r}")
        valid = {
            "asana_task", "asana_query", "asana_update", "asana_delete",
            "asana_complete", "asana_search", "link_request", "ata", "chat",
        }
        return intent if intent in valid else "chat"
    except Exception as e:
        bot_logger.warning(f"[BOT] Falha na classificação de intent via Gemini: {e}")
        return "chat"


def _extract_function_calls(response) -> list:
    """Extrai function_calls de forma robusta da resposta do Gemini."""
    try:
        if hasattr(response, "function_calls") and response.function_calls:
            return list(response.function_calls)
    except Exception:
        pass

    calls = []
    try:
        if hasattr(response, "parts") and response.parts:
            for part in response.parts:
                if hasattr(part, "function_call") and part.function_call:
                    calls.append(part.function_call)
            return calls
    except Exception:
        pass

    try:
        if hasattr(response, "candidates") and response.candidates:
            first = response.candidates[0]
            if hasattr(first, "content") and first.content and hasattr(first.content, "parts") and first.content.parts:
                for part in first.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        calls.append(part.function_call)
    except Exception:
        pass

    return calls


async def process_user_message(phone: str, message: str) -> str:
    """
    Processa uma mensagem do usuário com histórico de conversa como contexto.
    """
    bot_logger.info(f"[BOT] Processando mensagem de {phone} | tamanho: {len(message)} chars")

    instance = get_current_instance()
    instance_id = instance.get("id", "default")
    model = _get_model_with_tools()

    if not model:
        bot_logger.error("[BOT] GEMINI_API_KEY não configurada")
        return "Desculpe, estou com um problema técnico no momento. Tente novamente em breve."

    # Carrega histórico da conversa
    history = await get_conversation_history(phone, limit=10, instance_id=instance_id)
    bot_logger.debug(f"[BOT] Histórico carregado: {len(history)} mensagens anteriores")

    # Salva mensagem do usuário no Postgres
    await save_conversation_message(phone, "user", message, instance_id=instance_id)

    # Persona por instância — fallback para o padrão se vazio
    custom_prompt = (instance.get("system_prompt") or "").strip()
    assistant_name = (instance.get("assistant_name") or "").strip()
    system_prompt = custom_prompt if custom_prompt else SYSTEM_PROMPT_GABI

    ack = f"Entendido! Sou a {assistant_name}." if assistant_name else "Entendido! Estou pronta."

    gemini_history = []
    gemini_history.append({"role": "user", "parts": [system_prompt]})
    gemini_history.append({"role": "model", "parts": [ack]})

    for msg in history:
        role = msg["role"]
        gemini_role = "user" if role == "user" else "model"
        gemini_history.append({
            "role": gemini_role,
            "parts": [msg["content"]]
        })

    try:
        chat = model.start_chat(history=gemini_history)
        response = await chat.send_message_async(message)
        
        # Loop for handling function calls (Gemini Tools)
        function_calls = _extract_function_calls(response)
        while function_calls:
            function_responses = []
            for function_call in function_calls:
                name = function_call.name
                args = function_call.args
                bot_logger.info(f"[BOT] Executando ferramenta: {name} com argumentos: {args}")
                
                try:
                    if name == "list_my_tasks":
                        status = args.get("status", "todas")
                        result_str = await list_my_tasks(status=status)
                    elif name == "search_tasks_by_name":
                        query = args.get("query", "")
                        result_str = await search_tasks_by_name(query=query)
                    elif name == "add_comment_to_task_tool":
                        task_gid = args.get("task_gid", "")
                        comment_text = args.get("comment_text", "")
                        result_str = await add_comment_to_task_tool(task_gid=task_gid, comment_text=comment_text)
                    elif name == "complete_task_in_asana":
                        task_gid = args.get("task_gid", "")
                        result_str = await complete_task_in_asana(task_gid=task_gid)
                    elif name == "update_task_fields":
                        task_gid = args.get("task_gid", "")
                        name_val = args.get("name")
                        due_on_val = args.get("due_on")
                        notes_val = args.get("notes")
                        result_str = await update_task_fields(
                            task_gid=task_gid,
                            name=name_val,
                            due_on=due_on_val,
                            notes=notes_val
                        )
                    elif name == "delete_task_from_asana":
                        task_gid = args.get("task_gid", "")
                        result_str = await delete_task_from_asana(task_gid=task_gid)
                    elif name == "python_exec":
                        code = args.get("code", "")
                        result_str = await python_exec(code=code)
                    elif name == "toggle_briefings":
                        result_str = await toggle_briefings(
                            morning=args.get("morning"),
                            afternoon=args.get("afternoon"),
                            evening=args.get("evening")
                        )
                    elif name == "create_scheduled_task":
                        result_str = await create_scheduled_task(
                            name=args.get("name", ""),
                            cron_expression=args.get("cron_expression", ""),
                            code=args.get("code", "")
                        )
                    elif name == "create_webhook":
                        result_str = await create_webhook(
                            slug=args.get("slug", ""),
                            code=args.get("code", "")
                        )
                    else:
                        result_str = f"Erro: Ferramenta '{name}' não encontrada."
                except Exception as exc:
                    bot_logger.exception(f"[BOT] Erro ao executar ferramenta local {name}: {exc}")
                    result_str = f"Erro ao executar a ferramenta {name}: {str(exc)}"
                
                function_responses.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=name,
                            response={"result": result_str}
                        )
                    )
                )
            
            # Send the tool output back to Gemini
            response = await chat.send_message_async(
                genai.protos.Content(
                    role="user",
                    parts=function_responses
                )
            )
            function_calls = _extract_function_calls(response)
            
        result = response.text
        
        # Salva resposta no Postgres
        await save_conversation_message(phone, "assistant", result, instance_id=instance_id)
        bot_logger.info(f"[BOT] Resposta gerada para {phone} | tamanho: {len(result)} chars")

        return result
    except Exception as e:
        bot_logger.error(f"[BOT] Falha ao processar mensagem via Gemini: {e}")
        return "Desculpe, tive um problema ao processar sua mensagem."
