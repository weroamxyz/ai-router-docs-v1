import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';
import { i18n } from '@/lib/i18n';
import Image from 'next/image';
import type { LinkItemType } from 'fumadocs-ui/layouts/docs';
import { ExternalLink } from 'lucide-react';
import { siteBaseUrl, docTitle, logoSrc } from '@/lib/brand';

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

const logo = (
  <Image
    alt="logo"
    src={logoSrc}
    width={20}
    height={20}
    className="size-5"
    priority
    unoptimized
  />
);

export function baseOptions(locale: string): BaseLayoutProps {
  return {
    i18n,
    nav: {
      title: (
        <>
          {logo}
          <span className="font-medium in-[header]:text-[15px] [.uwu_&]:hidden">
            {docTitle[locale as keyof typeof docTitle] ?? docTitle.en}
          </span>
        </>
      ),
    },
  };
}
