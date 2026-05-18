interface FooterProps {
  lang: string;
}

export function Footer({ lang: _ }: FooterProps) {
  return (
    <footer className="border-fd-border bg-fd-card/30 mt-auto border-t backdrop-blur-sm">
      <div className="mx-auto max-w-[1400px] px-6 py-8">
        <p className="text-fd-muted-foreground text-xs">
          Copyright © 算力仓版权所有.
        </p>
      </div>
    </footer>
  );
}
