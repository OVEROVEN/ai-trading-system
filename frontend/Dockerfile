# Stage 1: builder
FROM node:18-alpine AS builder

# Define build-time arguments for use in the build stage
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL
ARG NEXT_PUBLIC_JWT_SECRET
ARG NEXT_PUBLIC_GOOGLE_CLIENT_ID
ARG NEXT_PUBLIC_ENVIRONMENT
ARG NEXT_PUBLIC_FEATURE_AI_ANALYSIS
ARG NEXT_PUBLIC_FEATURE_REDEMPTION
ARG NEXT_PUBLIC_FEATURE_TAIWAN_STOCKS

# Set them as environment variables for the build process
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_JWT_SECRET=$NEXT_PUBLIC_JWT_SECRET
ENV NEXT_PUBLIC_GOOGLE_CLIENT_ID=$NEXT_PUBLIC_GOOGLE_CLIENT_ID
ENV NEXT_PUBLIC_ENVIRONMENT=$NEXT_PUBLIC_ENVIRONMENT
ENV NEXT_PUBLIC_FEATURE_AI_ANALYSIS=$NEXT_PUBLIC_FEATURE_AI_ANALYSIS
ENV NEXT_PUBLIC_FEATURE_REDEMPTION=$NEXT_PUBLIC_FEATURE_REDEMPTION
ENV NEXT_PUBLIC_FEATURE_TAIWAN_STOCKS=$NEXT_PUBLIC_FEATURE_TAIWAN_STOCKS

WORKDIR /app

# Copy package files and install production dependencies
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

# Copy the rest of the source code
COPY . .

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Build the application
RUN npm run build

# Stage 2: runner
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs



# Copy the standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone .
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"
CMD ["node", "server.js"]
