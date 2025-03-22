# Use Node.js LTS image
FROM node:18-alpine AS build

# Set working directory
WORKDIR /weight/app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Accept `VITE_API_URL` from Docker Compose
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Build the app
RUN npm run build

# Use a lightweight web server for production
FROM nginx:alpine AS production

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx config
COPY nginx.template.conf /etc/nginx/nginx.template.conf
COPY entrypoint.sh /entrypoint.sh

# Set working directory in Nginx
WORKDIR /usr/share/nginx/html

# Copy built React app from the previous stage
COPY --from=build /weight/app/dist .

# Expose port 80
EXPOSE 80

# Start Nginx
ENTRYPOINT ["/entrypoint.sh"]