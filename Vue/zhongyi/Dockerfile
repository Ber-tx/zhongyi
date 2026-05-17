FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_SOFTWARE_MODE=true
ARG VITE_ENABLE_IDCARD=false
ARG VITE_ENABLE_PULSE=false

ENV VITE_SOFTWARE_MODE=${VITE_SOFTWARE_MODE}
ENV VITE_ENABLE_IDCARD=${VITE_ENABLE_IDCARD}
ENV VITE_ENABLE_PULSE=${VITE_ENABLE_PULSE}

RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
