FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d/default.conf

# ✅ Permisos al usuario nginx sobre los directorios que necesita
RUN chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx   && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid              && \
    chown nginx:nginx /var/run/nginx.pid

USER nginx
