const { execSync } = require('child_process');
const fs = require('fs');
try {
  const diff = execSync('git diff main..HEAD --name-only', { cwd: 'd:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/designer/frontend' }).toString();
  fs.writeFileSync('d:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/diff_files.txt', diff);
} catch (e) {
  fs.writeFileSync('d:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/diff_files.txt', e.toString() + e.stdout?.toString() + e.stderr?.toString());
}