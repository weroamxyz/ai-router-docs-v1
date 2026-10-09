'use client';

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ComponentProps,
  type ReactNode,
} from 'react';
import { ChevronRight } from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from 'fumadocs-ui/components/ui/collapsible';
import { cn } from '@/lib/cn';

type ParameterLocale = 'en' | 'zh';

const labels: Record<ParameterLocale, { required: string; optional: string }> =
  {
    en: { required: 'Required', optional: 'Optional' },
    zh: { required: '必填', optional: '可选' },
  };

const ParameterContext = createContext({
  depth: 0,
  locale: 'en' as ParameterLocale,
  optionalLabel: labels.en.optional,
  requiredLabel: labels.en.required,
});

export function ParameterTree({
  locale = 'en',
  optionalLabel,
  requiredLabel,
  className,
  ...props
}: ComponentProps<'div'> & {
  locale?: ParameterLocale;
  optionalLabel?: string;
  requiredLabel?: string;
}) {
  return (
    <ParameterContext.Provider
      value={{
        depth: 0,
        locale,
        optionalLabel: optionalLabel ?? labels[locale].optional,
        requiredLabel: requiredLabel ?? labels[locale].required,
      }}
    >
      <div
        className={cn(
          'not-prose bg-fd-card text-fd-card-foreground my-6 overflow-hidden rounded-xl border',
          className
        )}
        {...props}
      />
    </ParameterContext.Provider>
  );
}

export function ParameterChildren({
  className,
  ...props
}: ComponentProps<'div'>) {
  const context = useContext(ParameterContext);

  return (
    <ParameterContext.Provider value={{ ...context, depth: context.depth + 1 }}>
      <div
        className={cn(
          'not-prose border-fd-border mt-4 flex flex-col gap-2 border-s-2 ps-3',
          className
        )}
        {...props}
      />
    </ParameterContext.Provider>
  );
}

interface ParameterFieldProps
  extends Omit<ComponentProps<typeof Collapsible>, 'children' | 'open'> {
  children: ReactNode;
  id?: string;
  name: string;
  required?: boolean;
  type: string;
}

export function ParameterField({
  children,
  className,
  defaultOpen = false,
  id,
  name,
  onOpenChange,
  required = false,
  type,
  ...props
}: ParameterFieldProps) {
  const { depth, optionalLabel, requiredLabel } = useContext(ParameterContext);
  const [open, setOpen] = useState(defaultOpen);

  useEffect(() => {
    if (!id) return;

    const openForHash = () => {
      const hash = decodeURIComponent(window.location.hash.slice(1));
      if (hash === id || hash.startsWith(`${id}-`)) setOpen(true);
    };

    openForHash();
    window.addEventListener('hashchange', openForHash);
    return () => window.removeEventListener('hashchange', openForHash);
  }, [id]);

  return (
    <Collapsible
      {...props}
      className={cn(
        depth === 0
          ? 'border-fd-border border-b last:border-b-0'
          : 'border-fd-border bg-fd-background overflow-hidden rounded-lg border',
        className
      )}
      onOpenChange={(nextOpen) => {
        setOpen(nextOpen);
        onOpenChange?.(nextOpen);
      }}
      open={open}
    >
      <CollapsibleTrigger
        id={id}
        className="group hover:bg-fd-accent focus-visible:ring-fd-ring grid w-full grid-cols-[minmax(0,1fr)_auto] items-center gap-3 px-3 py-2.5 text-start focus-visible:ring-2 focus-visible:outline-none"
      >
        <span className="flex min-w-0 items-center gap-2">
          <ChevronRight className="text-fd-muted-foreground size-4 shrink-0 transition-transform group-data-[state=open]:rotate-90" />
          <code className="text-fd-primary truncate font-medium">{name}</code>
          <code className="text-fd-muted-foreground truncate text-xs">
            {type}
          </code>
        </span>
        <span
          className={cn(
            'rounded-full px-2 py-0.5 text-[11px] font-medium',
            required
              ? 'bg-fd-primary/10 text-fd-primary'
              : 'bg-fd-muted text-fd-muted-foreground'
          )}
        >
          {required ? requiredLabel : optionalLabel}
        </span>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="prose prose-no-margin border-fd-border border-t px-4 py-3 text-sm">
          {children}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
