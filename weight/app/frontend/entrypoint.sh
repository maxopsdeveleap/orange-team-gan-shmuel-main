#!/bin/sh

# Replace env vars in nginx.template.conf and save as nginx.conf
envsubst '${APP_NAME} ${APP_PORT}' < /etc/nginx/nginx.template.conf > /etc/nginx/conf.d/app.conf

# Start nginx
exec nginx -g 'daemon off;'
