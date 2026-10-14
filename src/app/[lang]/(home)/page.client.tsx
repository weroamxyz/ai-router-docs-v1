'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { cn } from '@/lib/cn';

const GrainGradient = dynamic(
  () => import('@paper-design/shaders-react').then((m) => m.GrainGradient),
  { ssr: false }
);

export function Hero() {
  const [showShaders, setShowShaders] = useState(false);

  useEffect(() => {
    const t = window.setTimeout(() => setShowShaders(true), 400);
    return () => window.clearTimeout(t);
  }, []);

  return (
    <>
      {/* Static fallback gradient */}
      <div
        className="absolute inset-0"
        style={{
          backgroundColor: '#060b18',
          backgroundImage: [
            'radial-gradient(ellipse 120% 80% at 10% 20%, rgba(168,85,247,.18), transparent 50%)',
            'radial-gradient(ellipse 100% 70% at 80% 30%, rgba(139,92,246,.16), transparent 50%)',
            'radial-gradient(ellipse 80% 60% at 50% 85%, rgba(192,132,252,.12), transparent 50%)',
          ].join(','),
        }}
      />

      {showShaders && (
        <GrainGradient
          className={cn('animate-fd-fade-in absolute inset-0 duration-1000')}
          colors={['#a855f7', '#8b5cf6', '#c084fc', '#00000000']}
          colorBack="#060b18"
          softness={1}
          intensity={0.55}
          noise={0.38}
          shape="corners"
        />
      )}
    </>
  );
}

export function Typewriter({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (done) return;
    if (displayed.length >= text.length) {
      setDone(true);
      return;
    }
    const t = setTimeout(
      () => setDisplayed(text.slice(0, displayed.length + 1)),
      90
    );
    return () => clearTimeout(t);
  }, [displayed, text, done]);

  return (
    <>
      {displayed}
      {!done && (
        <span className="ml-1 inline-block h-[0.85em] w-[3px] animate-pulse bg-current align-middle" />
      )}
      {done && (
        <span className="ml-2 inline-block size-3 animate-pulse rounded-full bg-violet-400 align-middle" />
      )}
    </>
  );
}
