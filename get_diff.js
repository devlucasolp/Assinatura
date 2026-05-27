const { execSync } = require('child_process');
const fs = require('fs');
const diff = execSync('git diff main..HEAD', { cwd: 'd:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/designer', maxBuffer: 1024 * 1024 * 10 }).toString();
fs.writeFileSync('d:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/diff.txt', diff);
