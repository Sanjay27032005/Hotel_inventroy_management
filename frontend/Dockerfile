FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Expose Vite's default dev server port
EXPOSE 5173

# Run the dev server and bind to all network interfaces
CMD ["npm", "run", "dev", "--", "--host"]
