FROM node:22-alpine AS build

RUN corepack enable

WORKDIR /app

COPY package.json pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/package.json
COPY packages/payments/package.json packages/payments/package.json
COPY packages/telegram/package.json packages/telegram/package.json

RUN pnpm install --no-frozen-lockfile

COPY apps/web apps/web
COPY packages/payments packages/payments
COPY packages/telegram packages/telegram

RUN pnpm --filter @peskovp/payments build && \
    pnpm --filter @peskovp/telegram build && \
    pnpm --filter @peskovp/web build

FROM node:22-alpine AS runtime

RUN corepack enable && addgroup -S app && adduser -S app -G app

WORKDIR /app

ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=3000

COPY --from=build /app/package.json /app/pnpm-workspace.yaml ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/apps/web ./apps/web
COPY --from=build /app/packages/payments ./packages/payments
COPY --from=build /app/packages/telegram ./packages/telegram

USER app

EXPOSE 3000

CMD ["pnpm", "--filter", "@peskovp/web", "start"]
