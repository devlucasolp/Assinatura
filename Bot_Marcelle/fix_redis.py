import sys
with open('integrations/redis_client.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('instance_id: str = "default"', 'instance_id: str | None = None')

with open('integrations/redis_client.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
