import { config } from 'dotenv';
config({ path: './designer/backend/.env' });

import { PrismaClient } from './designer/backend/node_modules/@prisma/client/index.js';

const prisma = new PrismaClient();

async function main() {
  const posts = await prisma.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 5
  });

  console.log(`Found ${posts.length} posts`);
  for (const p of posts) {
    console.log(`\n--- POST ${p.id} ---`);
    console.log(`Type: ${p.type}`);
    console.log(`PreviewUrl: ${p.previewUrl}`);
    console.log(`Content type:`, typeof p.content);
    if (p.content) {
      console.log(JSON.stringify(p.content).substring(0, 200));
    }
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
