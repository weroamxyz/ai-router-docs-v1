import {
  defineConfig,
  defineDocs,
  frontmatterSchema,
  metaSchema,
} from 'fumadocs-mdx/config';
import { resolveBrandTokens, localeFromPath } from './src/lib/brand';

// Remark plugin: resolve ((TOKEN)) placeholders in docs body (prose, code blocks,
// inline code, and JSX text/attributes). Locale is derived from the file path so a
// single ((BRAND)) renders as the right per-locale name.
function remarkBrandTokens() {
  return (tree: unknown, file: { path?: string }) => {
    const locale = localeFromPath(file.path ?? '');
    const walk = (node: Record<string, unknown>) => {
      if (typeof node.value === 'string') {
        node.value = resolveBrandTokens(node.value, locale);
      }
      // Markdown link/image nodes carry the target on `url` (and `title`).
      if (typeof node.url === 'string') {
        node.url = resolveBrandTokens(node.url, locale);
      }
      if (typeof node.title === 'string') {
        node.title = resolveBrandTokens(node.title, locale);
      }
      const attributes = node.attributes;
      if (Array.isArray(attributes)) {
        for (const attr of attributes) {
          if (attr && typeof attr.value === 'string') {
            attr.value = resolveBrandTokens(attr.value, locale);
          }
        }
      }
      const children = node.children;
      if (Array.isArray(children)) {
        for (const child of children) walk(child as Record<string, unknown>);
      }
    };
    walk(tree as Record<string, unknown>);
  };
}

// You can customise Zod schemas for frontmatter and `meta.json` here
// see https://fumadocs.dev/docs/mdx/collections
export const docs = defineDocs({
  dir: 'content/docs',
  docs: {
    // Resolve ((TOKEN)) placeholders in frontmatter title/description per locale.
    schema: (ctx) =>
      frontmatterSchema.transform((data) => {
        const locale = localeFromPath(ctx.path);
        return {
          ...data,
          title: resolveBrandTokens(data.title, locale),
          description: data.description
            ? resolveBrandTokens(data.description, locale)
            : data.description,
        };
      }),
    postprocess: {
      includeProcessedMarkdown: true,
    },
  },
  meta: {
    schema: metaSchema,
  },
});

export default defineConfig({
  // Enable last modified time from git
  lastModifiedTime: 'git',
  mdxOptions: {
    remarkPlugins: [remarkBrandTokens],
  },
});
