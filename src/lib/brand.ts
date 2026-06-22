// Single source of truth for brand identity.
//
// All values resolve from NEXT_PUBLIC_* env vars at build time, defaulting to the
// Unode (算力仓) brand. Switch brand per deployment by setting these env vars
// (e.g. the RoamAI Vercel project sets NEXT_PUBLIC_BRAND_NAME / _SITE_BASE_URL /
// _LOGO_SRC). The same content/code therefore serves both brands.
//
// Keep this module dependency-free: it is imported both by client components
// (so only NEXT_PUBLIC_* env is readable) and by source.config.ts (bundled by
// fumadocs-mdx) to resolve ((TOKEN)) placeholders in docs content.

type Locale = 'en' | 'zh' | 'ja';

const nameOverride = process.env.NEXT_PUBLIC_BRAND_NAME?.trim() || undefined;

export const siteBaseUrl =
  process.env.NEXT_PUBLIC_SITE_BASE_URL ?? 'https://www.unodetech.xyz';

// Host part of siteBaseUrl, e.g. "www.unodetech.xyz" — used in wss:// examples.
export const siteHost = siteBaseUrl.replace(/^https?:\/\//, '');

export const logoSrc = process.env.NEXT_PUBLIC_LOGO_SRC ?? '/assets/logo.png';

export const supportEmail =
  process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? 'support@unodetech.xyz';

// Brand name per locale (defaults: en/ja "Unode", zh "算力仓"). A single
// NEXT_PUBLIC_BRAND_NAME override applies to every locale (RoamAI has no
// separate Chinese name).
export const brandName: Record<Locale, string> = {
  en: nameOverride ?? 'Unode',
  ja: nameOverride ?? 'Unode',
  zh: nameOverride ?? '算力仓',
};

// Nav / documentation title per locale.
export const docTitle: Record<Locale, string> = {
  en: `${brandName.en} Docs`,
  ja: `${brandName.ja} Docs`,
  zh: nameOverride ? `${nameOverride} 文档` : '算力仓文档',
};

function asLocale(value: string): Locale {
  return value === 'zh' || value === 'ja' ? value : 'en';
}

// Derive locale from a content file path like ".../content/docs/zh/...".
export function localeFromPath(path: string): Locale {
  const match = path.replace(/\\/g, '/').match(/content\/docs\/([a-z]{2})\//);
  return match ? asLocale(match[1]) : 'en';
}

// Resolve ((TOKEN)) placeholders embedded in docs content for a given locale.
// The (( )) delimiter is inert in YAML frontmatter, Markdown/MDX, and code blocks
// alike (unlike %%, {{, or [[ which collide with one of them).
export function resolveBrandTokens(text: string, locale: string): string {
  if (!text.includes('((')) return text;
  const loc = asLocale(locale);
  return text
    .replaceAll('((SITE_URL))', siteBaseUrl)
    .replaceAll('((SITE_HOST))', siteHost)
    .replaceAll('((SUPPORT_EMAIL))', supportEmail)
    .replaceAll('((LOGO))', logoSrc)
    .replaceAll('((BRAND))', brandName[loc]);
}
