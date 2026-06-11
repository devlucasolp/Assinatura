"""
BOT - Handler de consultas ao Asana (leitura)

Permite que a Gabriela pergunte sobre suas tarefas e receba uma resposta
diretamente do Asana — sem precisar abrir o app.

Exemplos:
  "o que tenho para hoje?"
  "quais minhas tarefas atrasadas?"
  "me manda um resumo do que está aberto"
  "tem alguma coisa pra amanhã?"
  "qual o link da tarefa X?"
  "me manda o link da reunião com Marcelle"
"""

from datetime import date
from core.logger import bot_logger
from integrations.asana_client import (
    get_my_tasks,
    search_task_by_name,
)
from integrations.evolution_api import send_text_message
from integrations.redis_client import get_last_task


def _format_task_line(task: dict) -> str:
    name = task.get("name", "—")
    due = task.get("due_on", "")
    link = task.get("permalink_url", "")
    project = ""
    projects = task.get("projects", [])
    if projects:
        project = f" [{projects[0].get('name', '')}]" if projects[0].get("name") else ""

    parts = [f"• {name}"]
    if due:
        try:
            d = date.fromisoformat(due)
            parts[0] += f" ({d.strftime('%d/%m')}){project}"
        except ValueError:
            parts[0] += f" ({due}){project}"
    elif project:
        parts[0] += project

    if link:
        parts.append(f"  {link}")
    return "\n".join(parts)


async def handle_asana_query(sender_phone: str, text: str) -> None:
    """
    Lê tarefas do Asana e responde à Gabriela com um resumo relevante.
    Sempre usa assignee=me no workspace inteiro — bot é exclusivo da Gabi.
    """
    bot_logger.info(f"[BOT] Consulta Asana de {sender_phone}: {text[:60]!r}")

    lower = text.lower()
    today_str = date.today().strftime("%d/%m/%Y")

    try:
        # ── 1. Pedido de link de tarefa específica ──────────────────────────
        link_keywords = ["link", "url", "endereço", "acesso"]
        if any(w in lower for w in link_keywords):
            await _handle_link_query(sender_phone, text, lower)
            return

        # Atrasadas
        if any(w in lower for w in ["atrasad", "vencid", "passa", "atrasou", "overdue"]):
            tasks = await get_my_tasks(overdue_only=True)
            if not tasks:
                await send_text_message(to=sender_phone, text="Nenhuma tarefa atrasada.")
                return
            lines = [f"*Tarefas atrasadas* ({len(tasks)}):"]
            lines += [_format_task_line(t) for t in tasks[:15]]
            await send_text_message(to=sender_phone, text="\n".join(lines))
            return

        # Amanhã
        if any(w in lower for w in ["amanhã", "amanha", "próximo dia", "proximo dia"]):
            all_tasks = await get_my_tasks(days_ahead=1)
            tasks_tomorrow = [t for t in all_tasks if t.get("due_on", "") > date.today().isoformat()]
            if not tasks_tomorrow:
                await send_text_message(to=sender_phone, text="Nada para amanhã.")
                return
            lines = [f"*Para amanhã* ({len(tasks_tomorrow)}):"]
            lines += [_format_task_line(t) for t in tasks_tomorrow]
            await send_text_message(to=sender_phone, text="\n".join(lines))
            return

        # Hoje
        if any(w in lower for w in ["hoje", "dia", "agora"]):
            tasks = await get_my_tasks(days_ahead=0)
            if not tasks:
                await send_text_message(to=sender_phone, text=f"Nada com vencimento para hoje ({today_str}).")
                return
            lines = [f"*Para hoje* — {today_str} ({len(tasks)}):"]
            lines += [_format_task_line(t) for t in tasks]
            await send_text_message(to=sender_phone, text="\n".join(lines))
            return

        # ── 2. Resumo geral ─────────────────────────────────────────────────
        tasks_soon = await get_my_tasks(days_ahead=7)
        overdue = await get_my_tasks(overdue_only=True)

        sections = []
        if overdue:
            lines = [f"⚠️ *Atrasadas* ({len(overdue)}):"]
            lines += [_format_task_line(t) for t in overdue[:5]]
            if len(overdue) > 5:
                lines.append(f"  ...e mais {len(overdue) - 5}")
            sections.append("\n".join(lines))

        if tasks_soon:
            lines = [f"📅 *Próximos 7 dias* ({len(tasks_soon)}):"]
            lines += [_format_task_line(t) for t in tasks_soon[:10]]
            if len(tasks_soon) > 10:
                lines.append(f"  ...e mais {len(tasks_soon) - 10}")
            sections.append("\n".join(lines))

        if not sections:
            await send_text_message(to=sender_phone, text="Nenhuma tarefa com prazo nos próximos 7 dias.")
            return

        await send_text_message(to=sender_phone, text="\n\n".join(sections))

    except Exception as exc:
        bot_logger.exception(f"[BOT] Erro ao consultar Asana: {exc}")
        await send_text_message(
            to=sender_phone,
            text="Não consegui acessar o Asana agora. Tenta em instantes.",
        )


async def _handle_link_query(sender_phone: str, text: str, lower: str) -> None:
    """
    Tenta encontrar o link de uma tarefa pelo nome mencionado no texto.
    Fallback: última tarefa criada salva no Redis.
    """
    # Extrai possível nome de tarefa (tira as palavras de link e artigos)
    strip_words = [
        "qual o link", "me manda o link", "quero o link", "me passa o link",
        "link da tarefa", "link da reunião", "link do", "link da", "link de",
        "link", "url", "endereço", "acesso",
    ]
    query = lower
    for sw in strip_words:
        query = query.replace(sw, "")
    query = query.strip(" ?.,!")

    if query:
        results = await search_task_by_name(query)
        if results:
            if len(results) == 1:
                t = results[0]
                msg = f"*{t['name']}*\n{t.get('permalink_url', 'Link não disponível')}"
                await send_text_message(to=sender_phone, text=msg)
                return
            else:
                lines = [f"Encontrei {len(results)} tarefas parecidas:"]
                for t in results[:5]:
                    lines.append(f"• {t['name']}\n  {t.get('permalink_url', '')}")
                await send_text_message(to=sender_phone, text="\n".join(lines))
                return

    # Fallback: última tarefa criada no Redis
    last = await get_last_task(sender_phone)
    if last and last.get("link"):
        lines = [f"*{last['name']}*", f"Link: {last['link']}"]
        if last.get("project"):
            lines.insert(1, f"Projeto: {last['project']}")
        await send_text_message(to=sender_phone, text="\n".join(lines))
    else:
        await send_text_message(
            to=sender_phone,
            text="Não achei a tarefa. Me passa o nome exato e busco pra você.",
        )
