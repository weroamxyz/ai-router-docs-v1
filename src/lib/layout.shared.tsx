import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';
import { i18n } from '@/lib/i18n';
import Image from 'next/image';
import type { LinkItemType } from 'fumadocs-ui/layouts/docs';

export const linkItems: LinkItemType[] = [];

const logo = (
  <Image
    alt="logo"
    src="/assets/logo.png"
    width={20}
    height={20}
    className="size-5"
    priority
    unoptimized
  />
);

const brandName: Record<string, string> = {
  zh: '算力仓',
  en: 'ComputeVault',
};

export function baseOptions(locale: string): BaseLayoutProps {
  return {
    i18n,
    nav: {
      title: (
        <>
          {logo}
          <span className="font-medium in-[header]:text-[15px] [.uwu_&]:hidden">
            {brandName[locale] ?? 'ComputeVault'}
          </span>
        </>
      ),
    },
  };
}
