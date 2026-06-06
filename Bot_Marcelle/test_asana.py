import asyncio
import json
from integrations.asana_client import get_my_tasks, get_project_tasks, search_project_by_name, search_task_by_name

async def test_asana():
    print("Iniciando teste de conexão com o Asana...")
    try:
        print("\n1. Testando busca de tarefas do projeto...")
        project_tasks = await get_project_tasks()
        print(f"-> Sucesso! Encontradas {len(project_tasks)} tarefas no projeto configurado.")
        for i, task in enumerate(project_tasks[:3]):
            print(f"   - Tarefa {i+1}: {task.get('name')} (Status: {'Concluída' if task.get('completed') else 'Pendente'})")

        print("\n2. Testando busca de tarefas atribuídas a você (assignee=me)...")
        my_tasks = await get_my_tasks()
        print(f"-> Sucesso! Encontradas {len(my_tasks)} tarefas atribuídas a você.")
        for i, task in enumerate(my_tasks[:3]):
            print(f"   - Tarefa {i+1}: {task.get('name')} (Vencimento: {task.get('due_on')})")

        print("\n3. Testando pesquisa por uma tarefa genérica...")
        searched = await search_task_by_name("reunião")
        print(f"-> Sucesso! {len(searched)} resultados encontrados para 'reunião'.")
        for i, task in enumerate(searched[:3]):
            print(f"   - Encontrado {i+1}: {task.get('name')}")

    except Exception as e:
        print(f"\n[ERRO] Falha ao conectar com o Asana: {e}")

if __name__ == "__main__":
    asyncio.run(test_asana())
