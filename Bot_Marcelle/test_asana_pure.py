import os
import json
import urllib.request
import urllib.error

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        return {}
    
    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
    return env_vars

def test_asana():
    print("Iniciando teste de conexão com o Asana usando urllib...")
    env_vars = load_env()
    
    token = env_vars.get("ASANA_ACCESS_TOKEN")
    workspace = env_vars.get("ASANA_WORKSPACE_GID")
    project = env_vars.get("ASANA_PROJECT_GID")
    
    if not token:
        print("[ERRO] ASANA_ACCESS_TOKEN não encontrado no .env")
        return
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    base_url = "https://app.asana.com/api/1.0"
    
    try:
        # Teste 1: Buscar tarefas do projeto
        if project:
            print("\n1. Testando busca de tarefas do projeto...")
            url = f"{base_url}/projects/{project}/tasks?opt_fields=name,completed&completed_since=now"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                tasks = data.get("data", [])
                print(f"-> Sucesso! Encontradas {len(tasks)} tarefas no projeto configurado.")
                for i, task in enumerate(tasks[:3]):
                    status = "Concluída" if task.get("completed") else "Pendente"
                    print(f"   - Tarefa {i+1}: {task.get('name')} (Status: {status})")
        else:
            print("\n1. Pulo: ASANA_PROJECT_GID não configurado.")
            
        # Teste 2: Buscar tarefas do usuário (assignee=me)
        if workspace:
            print("\n2. Testando busca de tarefas atribuídas a você (assignee=me)...")
            url = f"{base_url}/tasks?assignee=me&workspace={workspace}&opt_fields=name,due_on&completed_since=now&limit=10"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                my_tasks = data.get("data", [])
                print(f"-> Sucesso! Encontradas {len(my_tasks)} tarefas atribuídas a você.")
                for i, task in enumerate(my_tasks[:3]):
                    print(f"   - Tarefa {i+1}: {task.get('name')} (Vencimento: {task.get('due_on')})")
                    
            # Teste 3: Pesquisa por tarefa genérica "reunião"
            print("\n3. Testando pesquisa por uma tarefa genérica 'reunião'...")
            url = f"{base_url}/workspaces/{workspace}/typeahead?resource_type=task&query=reuni%C3%A3o&opt_fields=name"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                searched = data.get("data", [])
                print(f"-> Sucesso! {len(searched)} resultados encontrados para 'reunião'.")
                for i, task in enumerate(searched[:3]):
                    print(f"   - Encontrado {i+1}: {task.get('name')}")
        else:
            print("\n2 e 3. Pulo: ASANA_WORKSPACE_GID não configurado.")

    except urllib.error.HTTPError as e:
        print(f"\n[ERRO HTTP] Falha ao conectar com o Asana: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"\n[ERRO] Falha inesperada: {e}")

if __name__ == "__main__":
    test_asana()
