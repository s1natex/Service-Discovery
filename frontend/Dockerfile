FROM node:20 AS build
WORKDIR /app

COPY package*.json ./

RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

FROM nginx:alpine
RUN addgroup -S -g 10001 app \
 && adduser -S -u 10001 -G app app \
 && mkdir -p /var/cache/nginx /var/run /var/log/nginx /tmp

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

RUN chown -R app:app /usr/share/nginx/html /etc/nginx /var/cache/nginx /var/run /var/log/nginx /tmp
USER 10001

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=2s --retries=5 --start-period=5s \
  CMD wget -qO- http://127.0.0.1:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
