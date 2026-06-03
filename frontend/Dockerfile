FROM node:22-slim AS deps

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

FROM node:22-slim AS builder

WORKDIR /app
ARG NEXT_PUBLIC_HELIOS_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_HELIOS_WS_URL=ws://localhost:8000/events
ARG NEXT_PUBLIC_HELIOS_API_KEY=
ENV NEXT_PUBLIC_HELIOS_API_URL=$NEXT_PUBLIC_HELIOS_API_URL
ENV NEXT_PUBLIC_HELIOS_WS_URL=$NEXT_PUBLIC_HELIOS_WS_URL
ENV NEXT_PUBLIC_HELIOS_API_KEY=$NEXT_PUBLIC_HELIOS_API_KEY
COPY --from=deps /app/node_modules ./node_modules
COPY frontend ./
RUN npm run build

FROM node:22-slim AS runner

ENV NODE_ENV=production
WORKDIR /app
COPY --from=builder /app ./

EXPOSE 3000

CMD ["npm", "run", "start"]
