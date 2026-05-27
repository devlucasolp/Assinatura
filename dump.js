const cp = require('child_process');
const fs = require('fs');
try {
  const out = cp.execSync('git log -n 3 -p designer/frontend/src/components/Fabrica/DesignRenderer.tsx', { encoding: 'utf8' });
  fs.writeFileSync('D:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/dump.txt', out);
} catch (e) {
  fs.writeFileSync('D:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/dump.txt', e.toString());
}
