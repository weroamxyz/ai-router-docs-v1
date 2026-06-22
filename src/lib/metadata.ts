import type { Metadata } from 'next';
import { siteBaseUrl, brandName, logoSrc } from './brand';

export function createMetadata(override: Metadata): Metadata {
  return {
    ...override,
    icons: {
      icon: '/favicon.ico',
      shortcut: '/favicon.ico',
      apple: logoSrc,
    },
    openGraph: {
      title: override.title ?? undefined,
      description: override.description ?? undefined,
      url: siteBaseUrl,
      images: logoSrc,
      siteName: brandName.zh,
      type: 'website',
      ...override.openGraph,
    },
    twitter: {
      card: 'summary_large_image',
      title: override.title ?? undefined,
      description: override.description ?? undefined,
      images: logoSrc,
      ...override.twitter,
    },
  };
}

export const baseUrl =
  process.env.NODE_ENV === 'development' ||
  !process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? new URL('http://localhost:3000')
    : new URL(`https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`);
