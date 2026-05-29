const copyright: Record<string, string> = {
  zh: 'Copyright © 算力仓版权所有.',
  en: '© 2025 Unode. All rights reserved.',
  ja: '© 2025 Unode. All rights reserved.',
};

interface FooterProps {
  lang: string;
}

export function Footer({ lang }: FooterProps) {
  return (
    <footer className="border-fd-border bg-fd-card/30 mt-auto border-t backdrop-blur-sm">
      <div className="mx-auto max-w-[1400px] px-6 py-8">
        <p className="text-fd-muted-foreground text-xs">
          {copyright[lang] ?? copyright.en}
        </p>
      </div>
    </footer>
  );
}
