import Link from 'next/link';
import { BookOpen, Code2 } from 'lucide-react';
import { Hero, Typewriter } from './page.client';
import { getLocalePath, i18n } from '@/lib/i18n';

// ─── Content ────────────────────────────────────────────────────────────────

const content = {
  zh: {
    typewriterText: '简化 AI 开发流程',
    subtitle: '新一代大模型网关与 AI 资产管理系统',
    stats: [
      { number: '30+', label: 'AI 服务商' },
      { number: '100%', label: 'OpenAI 兼容' },
      { number: '100+', label: '海量模型支持' },
    ],
    features: [
      { icon: '🚀', text: '一键部署，快速接入' },
      { icon: '💰', text: '灵活计费，成本可控' },
      { icon: '🛡️', text: '安全稳定，高可用性' },
    ],
    arch: {
      client: '客户端应用',
      gateway: '算力仓网关',
      models: 'AI 模型',
      chips: [
        '🔒 用户管理', '⚖️ 负载均衡', '🧭 格式转换',
        '📊 成本追踪', '🚦 速率限制', '📝 日志记录',
        '💰 配额管理', '🔄 故障重试', '💳 在线充值',
      ],
    },
    getStarted: '开始使用',
    apiDocs: '接口文档',
  },
  en: {
    typewriterText: 'Simplify AI Development',
    subtitle: 'Next-Gen LLM Gateway & AI Asset Management Platform',
    stats: [
      { number: '30+', label: 'AI Providers' },
      { number: '100%', label: 'OpenAI Compatible' },
      { number: '100+', label: 'Many Models' },
    ],
    features: [
      { icon: '🚀', text: 'One-click deploy, rapid integration' },
      { icon: '💰', text: 'Flexible pricing, cost-effective' },
      { icon: '🛡️', text: 'Secure & highly available' },
    ],
    arch: {
      client: 'Client App',
      gateway: 'Unode Gateway',
      models: 'AI Models',
      chips: [
        '🔒 Auth', '⚖️ Load Balance', '🧭 Format Convert',
        '📊 Cost Track', '🚦 Rate Limit', '📝 Logging',
        '💰 Quota', '🔄 Failover', '💳 Recharge',
      ],
    },
    getStarted: 'Get Started',
    apiDocs: 'API Docs',
  },
  ja: {
    typewriterText: 'AI開発を簡略化',
    subtitle: '次世代LLMゲートウェイ & AI資産管理プラットフォーム',
    stats: [
      { number: '30+', label: 'AIプロバイダー' },
      { number: '100%', label: 'OpenAI互換' },
      { number: '100+', label: '海量モデル対応' },
    ],
    features: [
      { icon: '🚀', text: 'ワンクリックデプロイ、迅速な統合' },
      { icon: '💰', text: '柔軟な価格設定、コスト効率' },
      { icon: '🛡️', text: '安全で高可用性' },
    ],
    arch: {
      client: 'クライアントアプリ',
      gateway: 'Unodeゲートウェイ',
      models: 'AIモデル',
      chips: [
        '🔒 認証', '⚖️ 負荷分散', '🧭 フォーマット変換',
        '📊 コスト追跡', '🚦 速率制限', '📝 ログ記録',
        '💰 クォータ', '🔄 フェイルオーバー', '💳 充電',
      ],
    },
    getStarted: 'はじめに',
    apiDocs: 'APIドキュメント',
  },
} as const;

// ─── Arrow SVG ───────────────────────────────────────────────────────────────

function ArrowRight() {
  return (
    <svg
      className="size-5 shrink-0 text-white/30"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M13 7l5 5m0 0l-5 5m5-5H6"
      />
    </svg>
  );
}

function DashedArrow() {
  return (
    <svg
      className="h-3 w-12 shrink-0 text-white/30"
      viewBox="0 0 100 12"
      aria-hidden="true"
    >
      <path
        d="M10 6 H90"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeDasharray="4 4"
        fill="none"
      />
      <path d="M10,6 L16,3 L16,9 Z" fill="currentColor" />
      <path d="M90,6 L84,3 L84,9 Z" fill="currentColor" />
    </svg>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default async function Page({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  const c = content[lang as keyof typeof content] ?? content.zh;

  return (
    <main className="relative overflow-hidden bg-[#060b18]">
      {/* ── Background ── */}
      <Hero />

      {/* ── Content ── */}
      <div className="relative z-10 mx-auto flex max-w-4xl flex-col items-center px-4 pt-20 pb-24 text-center">

        {/* Title */}
        <h1 className="text-5xl font-bold leading-tight tracking-tight text-white md:text-6xl lg:text-7xl">
          <Typewriter text={c.typewriterText} />
        </h1>

        {/* Subtitle badge */}
        <p className="mt-6 rounded-full border border-sky-500/30 bg-sky-500/10 px-5 py-2 text-sm font-medium text-sky-300/90 backdrop-blur-sm md:text-base">
          {c.subtitle}
        </p>

        {/* Stats */}
        <div className="mt-10 flex items-center gap-10 md:gap-16">
          {c.stats.map((stat) => (
            <div key={stat.label} className="flex flex-col items-center gap-1">
              <span className="text-3xl font-bold text-white md:text-4xl">
                {stat.number}
              </span>
              <span className="text-xs text-white/45 md:text-sm">
                {stat.label}
              </span>
            </div>
          ))}
        </div>

        {/* Feature pills */}
        <div className="mt-7 flex flex-wrap justify-center gap-3">
          {c.features.map((f) => (
            <span
              key={f.text}
              className="flex items-center gap-2 rounded-full border border-white/20 bg-white/8 px-4 py-2 text-sm text-white/75 backdrop-blur-sm"
            >
              {f.icon} {f.text}
            </span>
          ))}
        </div>

        {/* ── Architecture Diagram ── */}
        <div className="mt-12 w-full">
          {/* Three-node flow */}
          <div className="flex items-center justify-center gap-2 md:gap-4">

            {/* Client node */}
            <div className="flex min-w-[80px] flex-col items-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-3 py-4 backdrop-blur-sm md:min-w-[110px] md:px-5">
              <span className="text-3xl md:text-4xl">🧑‍💻</span>
              <span className="text-center text-[11px] leading-tight text-white/60 md:text-xs">
                {c.arch.client}
              </span>
            </div>

            <ArrowRight />

            {/* Gateway node */}
            <div className="flex flex-1 flex-col items-center gap-3 rounded-2xl border border-sky-500/35 bg-sky-500/8 px-4 py-4 backdrop-blur-sm md:px-6">
              <div className="flex items-center gap-2">
                <span className="text-lg">⚡</span>
                <span className="font-semibold text-sky-300 text-sm md:text-base">
                  {c.arch.gateway}
                </span>
              </div>
              <div className="grid w-full grid-cols-3 gap-1.5">
                {c.arch.chips.map((chip) => (
                  <span
                    key={chip}
                    className="rounded-lg bg-white/8 px-1.5 py-1.5 text-center text-[10px] leading-tight text-white/55 md:text-[11px]"
                  >
                    {chip}
                  </span>
                ))}
              </div>
            </div>

            <ArrowRight />

            {/* AI Models node */}
            <div className="flex min-w-[80px] flex-col items-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-3 py-4 backdrop-blur-sm md:min-w-[110px] md:px-5">
              <span className="text-3xl md:text-4xl">🤖</span>
              <span className="text-center text-[11px] leading-tight text-white/60 md:text-xs">
                {c.arch.models}
              </span>
            </div>
          </div>

          {/* Provider row */}
          <div className="mt-4 flex items-center justify-center gap-2">
            {(['Gemini', 'OpenAI', 'Claude'] as const).map((name, i) => (
              <div key={name} className="flex items-center gap-2">
                {i > 0 && <DashedArrow />}
                <span className="rounded-lg border border-white/15 bg-white/5 px-3 py-1.5 text-xs text-white/50 md:text-sm">
                  {name}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Action buttons */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            href={getLocalePath(lang, 'docs')}
            className="inline-flex items-center gap-2 rounded-full bg-sky-500 px-6 py-3 font-medium text-white transition-colors hover:bg-sky-400"
          >
            <BookOpen className="size-4" />
            {c.getStarted}
          </Link>
          <Link
            href={getLocalePath(lang, 'docs/api')}
            className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/10 px-6 py-3 font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/20"
          >
            <Code2 className="size-4" />
            {c.apiDocs}
          </Link>
        </div>
      </div>
    </main>
  );
}

export async function generateStaticParams() {
  return i18n.languages.map((lang) => ({ lang }));
}
