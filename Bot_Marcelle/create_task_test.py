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

def create_task():
    env_vars = load_env()
    token = env_vars.get("ASANA_ACCESS_TOKEN")
    workspace = env_vars.get("ASANA_WORKSPACE_GID")
    project = env_vars.get("ASANA_PROJECT_GID")
    
    if not token or not project:
        print("[ERRO] Faltando token ou projeto no .env")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    base_url = "https://app.asana.com/api/1.0"
    
    # Buscar Gabriela Maia pelo Typeahead
    assignee_gid = None
    try:
        url = f"{base_url}/workspaces/{workspace}/typeahead?resource_type=user&query=gabriela&opt_fields=name,email"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            users = data.get("data", [])
            for u in users:
                if "gabriela" in u.get("name", "").lower() or "maia" in u.get("name", "").lower():
                    assignee_gid = u.get("gid")
                    print(f"-> Usuário encontrado para assignee: {u.get('name')} (GID: {assignee_gid})")
                    break
    except Exception as e:
        print(f"Aviso: Erro ao buscar usuário: {e}")
        
    if not assignee_gid:
        print("-> Usuário 'gabriela maia' não encontrado via API. Usando 'me' (dono do token) como assignee.")
        assignee_gid = "me"

    print(f"\nCriando a tarefa 'teste cafe da manha' no projeto {project}...")
    task_data = {
        "data": {
            "name": "teste cafe da manha",
            "projects": [project],
            "assignee": assignee_gid
        }
    }
    
    try:
        req = urllib.request.Request(
            f"{base_url}/tasks?opt_fields=name,permalink_url", 
            data=json.dumps(task_data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            task = data.get("data", {})
            print(f"\n✅ Tarefa criada com sucesso!")
            print(f"ID: {task.get('gid')}")
            print(f"Nome: {task.get('name')}")
            print(f"Link: {task.get('permalink_url')}")
    except urllib.error.HTTPError as e:
        print(f"\n[ERRO HTTP] {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"\n[ERRO] Falha inesperada: {e}")
        
if __name__ == "__main__":
    create_task()
