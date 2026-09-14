# new-api-docs-v1

A Next.js documentation site for New API.

## Development

Run the development server:

```bash
bun install

bun dev
```

Open http://localhost:3000 with your browser to see the result.

## Build

Build the application for production:

```bash
bun run build
```

## OpenAPI Generation

Generate the per-endpoint OpenAPI files and Chinese API pages with:

```bash
bun run generate:openapi
```

Endpoint metadata is fetched from Apifox. Version-controlled corrections in
`scripts/config/http-endpoint-overrides.json` are applied by endpoint ID after
the fetch. Generation fails when a configured endpoint ID is no longer present,
so upstream changes cannot silently remove a documented contract. English and
Japanese generated pages are maintained by the translation workflow and are not
deleted by this command.

## Project Structure

| Path                      | Description                  |
| ------------------------- | ---------------------------- |
| `app/(home)`              | Landing page and home pages  |
| `app/[lang]/docs`         | Documentation pages (i18n)   |
| `app/api/search/route.ts` | Search API endpoint          |
| `content/docs/`           | Documentation content (MDX)  |
| `lib/source.ts`           | Content source configuration |

## Learn More

- [Next.js Documentation](https://nextjs.org/docs) - Next.js features and API
