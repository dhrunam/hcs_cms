# ─── Build stage ─────────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Copy source and build
COPY . .
RUN npm run build -- --configuration=production

# ─── Runtime stage (nginx) ───────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Copy built Angular app
COPY --from=builder /app/dist/hcs-cms/browser /usr/share/nginx/html

# Custom nginx config for Angular routing (HTML5 pushState)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
