import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';
import { i18n } from '@/lib/i18n';
import type { LinkItemType } from 'fumadocs-ui/layouts/docs';
import { ExternalLink } from 'lucide-react';
import { siteBaseUrl } from '@/lib/brand';

const dashboardLabel: Record<string, string> = {
  en: 'Console',
  zh: '控制台',
  ja: 'コンソール',
};

export function linkItems(locale: string): LinkItemType[] {
  const label = dashboardLabel[locale] ?? dashboardLabel.en;
  return [
    {
      type: 'custom',
      children: (
        <a
          href={`${siteBaseUrl}/console?lang=${locale}`}
          target="_blank"
          rel="noreferrer noopener"
          className="inline-flex items-center gap-1 p-2 text-sm text-fd-muted-foreground transition-colors hover:text-fd-accent-foreground [&_svg]:size-3.5"
        >
          {label}
          <ExternalLink />
        </a>
      ),
    },
  ];
}

export function baseOptions(locale: string): BaseLayoutProps {
  return {
    i18n,
    nav: {
      title: (
        <img
          src="/logo-text.webp"
          alt="Unode"
          className="block h-5 w-auto"
        />
      ),
    },
  };
}
