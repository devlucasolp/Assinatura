import { generateDesign } from './designer/backend/src/lib/nanoBanana.ts';
import fs from 'fs';

async function test() {
  try {
    const slides = await generateDesign('teste', 'Marca: Teste\nSlides: 1', 'carousel', { width: 1080, height: 1080 });
    fs.writeFileSync('D:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/test_nano_out.json', JSON.stringify(slides, null, 2));
  } catch (e) {
    fs.writeFileSync('D:/Códigos/Tzolkin/Projetos/Projeto Assinatura/Assinatura/test_nano_out.json', e.toString());
  }
}
test();