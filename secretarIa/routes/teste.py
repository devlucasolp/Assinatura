from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

from core.logger import system_logger
from core.context import current_instance
from integrations.postgres import get_instance
from bot.llm.gemini_chat import process_user_message

router = APIRouter(prefix="/teste", tags=["Teste WS"])

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gabi Bot — Chat de Teste</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: radial-gradient(circle at top left, #1a1a24, #000000 70%);
            --surface: rgba(20, 20, 25, 0.6);
            --border: rgba(255, 255, 255, 0.08);
            --text: #ffffff;
            --text-secondary: #a1a1a1;
            --accent: #ffffff;
            --primary-gradient: linear-gradient(135deg, #ffffff 0%, #a1a1aa 100%);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-gradient); color: var(--text); display: flex; flex-direction: column; height: 100vh; }
        
        .topbar { background: rgba(10, 10, 12, 0.5); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }
        .brand { font-weight: 600; display: flex; align-items: center; gap: 8px; font-size: 15px; }
        .controls { display: flex; gap: 12px; align-items: center; }
        select, input, button { background: rgba(0,0,0,0.4); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; font-family: 'Inter', sans-serif; outline: none; transition: 0.3s; }
        select:focus, input:focus { border-color: var(--accent); background: rgba(0,0,0,0.8); box-shadow: 0 0 0 2px rgba(255,255,255,0.1); }
        button { cursor: pointer; font-weight: 600; }
        button:hover:not(:disabled) { transform: translateY(-1px); border-color: rgba(255,255,255,0.3); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .chat-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; max-width: 800px; margin: 0 auto; width: 100%; border-left: 1px solid var(--border); border-right: 1px solid var(--border); background: rgba(0,0,0,0.2); backdrop-filter: blur(10px); }
        .messages { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
        
        .msg { max-width: 80%; padding: 14px 18px; border-radius: 14px; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .msg.user { background: var(--surface); align-self: flex-end; border-bottom-right-radius: 4px; border: 1px solid var(--border); backdrop-filter: blur(5px); }
        .msg.bot { background: rgba(255,255,255,0.05); align-self: flex-start; border-top-left-radius: 4px; border: 1px solid var(--border); backdrop-filter: blur(5px); }
        .msg.system { text-align: center; color: var(--text-secondary); font-size: 0.8rem; align-self: center; background: transparent; box-shadow: none; border: none; }
        
        .input-area { padding: 20px 24px; border-top: 1px solid var(--border); background: rgba(10,10,12,0.6); display: flex; gap: 12px; backdrop-filter: blur(10px); }
        .input-area input { flex: 1; border-radius: 20px; padding: 12px 20px; }
        .btn-send { background: var(--primary-gradient); color: #000; border: none; border-radius: 20px; padding: 10px 24px; box-shadow: 0 4px 15px rgba(255,255,255,0.1); }
        .btn-send:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <header class="topbar">
        <div class="brand">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            Gabi Bot — Teste
        </div>
        <div class="controls">
            <select id="instanceSelect"><option value="">Carregando...</option></select>
            <input type="text" id="phoneInput" placeholder="Seu Telefone (Fictício)" value="5511999990000" style="width: 180px;">
            <button id="connectBtn">Conectar</button>
        </div>
    </header>

    <main class="chat-container">
        <div class="messages" id="messages">
            <div class="msg system">Selecione a instância e conecte para testar.</div>
        </div>
        <form class="input-area" id="chatForm">
            <input type="text" id="messageInput" placeholder="Digite sua mensagem..." disabled autocomplete="off">
            <button type="submit" id="sendBtn" class="btn-send" disabled>Enviar</button>
        </form>
    </main>

    <script>
        const instanceSelect = document.getElementById('instanceSelect');
        const phoneInput = document.getElementById('phoneInput');
        const connectBtn = document.getElementById('connectBtn');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const chatForm = document.getElementById('chatForm');
        const messagesDiv = document.getElementById('messages');
        
        let ws = null;

        // Load instances
        fetch('/api/instances')
            .then(res => res.json())
            .then(data => {
                instanceSelect.innerHTML = '';
                if(data.length === 0) {
                    instanceSelect.innerHTML = '<option value="">Nenhuma instância</option>';
                    return;
                }
                data.forEach(inst => {
                    const opt = document.createElement('option');
                    opt.value = inst.id;
                    opt.textContent = `${inst.name} (${inst.id})`;
                    instanceSelect.appendChild(opt);
                });
            })
            .catch(e => {
                instanceSelect.innerHTML = '<option value="">Erro ao carregar</option>';
            });

        function appendMessage(sender, text) {
            const el = document.createElement('div');
            el.className = `msg ${sender}`;
            el.textContent = text;
            messagesDiv.appendChild(el);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        connectBtn.addEventListener('click', () => {
            if (ws) {
                ws.close();
                return;
            }

            const instanceId = instanceSelect.value;
            const phone = phoneInput.value.trim();
            if(!instanceId || !phone) {
                alert('Selecione uma instância e informe um telefone.');
                return;
            }

            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/teste/ws/${instanceId}/${phone}`;
            
            appendMessage('system', `Conectando a ${instanceId}...`);
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                appendMessage('system', 'Conectado! Pode começar a conversar.');
                connectBtn.textContent = 'Desconectar';
                messageInput.disabled = false;
                sendBtn.disabled = false;
                instanceSelect.disabled = true;
                phoneInput.disabled = true;
                messageInput.focus();
            };

            ws.onmessage = (event) => {
                appendMessage('bot', event.data);
            };

            ws.onclose = () => {
                appendMessage('system', 'Desconectado.');
                ws = null;
                connectBtn.textContent = 'Conectar';
                messageInput.disabled = true;
                sendBtn.disabled = true;
                instanceSelect.disabled = false;
                phoneInput.disabled = false;
            };

            ws.onerror = (err) => {
                console.error(err);
                appendMessage('system', 'Erro na conexão WebSocket.');
            };
        });

        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if(!ws || ws.readyState !== WebSocket.OPEN) return;
            
            const text = messageInput.value.trim();
            if(!text) return;
            
            appendMessage('user', text);
            ws.send(text);
            messageInput.value = '';
        });
    </script>
</body>
</html>
"""

@router.get("", response_class=HTMLResponse)
async def get_test_chat():
    """Retorna a interface HTML do chat de teste."""
    return HTMLResponse(HTML_CONTENT)


@router.websocket("/ws/{instance_id}/{phone}")
async def websocket_chat(websocket: WebSocket, instance_id: str, phone: str):
    """
    Endpoint WebSocket para o chat de teste.
    Ele emula o comportamento do fluxo do WhatsApp chamando process_user_message diretamente.
    """
    await websocket.accept()
    
    # Valida e seta a instância
    inst = await get_instance(instance_id)
    if not inst:
        await websocket.send_text(f"Erro: Instância '{instance_id}' não encontrada no banco.")
        await websocket.close(code=1008)
        return
        
    # Injeta a instância no ContextVar para esta conexão
    current_instance.set(inst)
    system_logger.info(f"[WS TESTE] Conexão iniciada | instance: {instance_id} | phone: {phone}")

    try:
        while True:
            data = await websocket.receive_text()
            system_logger.debug(f"[WS TESTE] Mensagem recebida de {phone}: {data}")
            
            try:
                # O processamento da IA
                response = await process_user_message(phone, data)
                await websocket.send_text(response)
            except Exception as e:
                system_logger.exception(f"[WS TESTE] Erro ao processar: {e}")
                await websocket.send_text(f"Erro interno da IA: {str(e)}")
                
    except WebSocketDisconnect:
        system_logger.info(f"[WS TESTE] Conexão encerrada | phone: {phone}")
    except Exception as e:
        system_logger.error(f"[WS TESTE] Erro inesperado no socket: {e}")
        try:
            await websocket.close()
        except:
            pass
