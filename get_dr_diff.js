const cp = require('child_process');
const fs = require('fs');
try {
  const log = cp.execSync('git log -p -2 designer/frontend/src/components/Fabrica/DesignRenderer.tsx', { encoding: 'utf8' });
  fs.writeFileSync('diff_design_renderer.txt', log);
} catch (e) {
  fs.writeFileSync('diff_design_renderer.txt', e.toString());
}
