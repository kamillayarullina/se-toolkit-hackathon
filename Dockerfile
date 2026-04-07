FROM node:20-alpine

RUN apk add --no-cache curl

WORKDIR /app

RUN mkdir -p /app/data

COPY package*.json ./

RUN npm ci --only=production

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/tas || exit 1

CMD ["node", "server.js"]
