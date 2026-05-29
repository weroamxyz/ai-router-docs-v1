import { source } from '@/lib/source';
import { createFromSource } from 'fumadocs-core/search/server';
import { flattenTree } from 'fumadocs-core/page-tree';
import type { Root } from 'fumadocs-core/page-tree';
import { createTokenizer as createMandarinTokenizer } from '@orama/tokenizers/mandarin';

const filteredSource = {
  ...source,
  getLanguages: () =>
    source.getLanguages().map((entry) => {
      const tree = (source.pageTree as Record<string, Root>)[entry.language];
      const visibleUrls = new Set(
        flattenTree(tree?.children ?? []).map((item) => item.url),
      );
      return {
        ...entry,
        pages: entry.pages.filter((page) => visibleUrls.has(page.url)),
      };
    }),
} as typeof source;

export const { GET } = createFromSource(filteredSource, {
  localeMap: {
    en: { language: 'english' },
    zh: {
      components: { tokenizer: createMandarinTokenizer() },
      search: { threshold: 0, tolerance: 0 },
    },
  },
});
