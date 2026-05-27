import base64
from PIL import Image

try:
    img = Image.open('Captura de tela 2026-05-06 082219.png')
    # Crop or resize to make it reasonable
    img.thumbnail((300, 300))
    img.save('assinatura_thumb.png')
    
    with open('assinatura_thumb.png', 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
        
    svg_content = f'''<svg width="{img.width}" height="{img.height}" xmlns="http://www.w3.org/2000/svg">
  <image href="data:image/png;base64,{b64}" width="100%" height="100%"/>
</svg>'''

    with open('designer/frontend/public/assinatura-logo.svg', 'w') as f:
        f.write(svg_content)
    print("SVG criado com sucesso!")
except Exception as e:
    print("Erro:", e)
