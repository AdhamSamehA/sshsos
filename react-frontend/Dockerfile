FROM node:14

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install remaining dependencies
RUN npm install

# Copy the rest of the app's source code
COPY . .

# Build the React app
RUN npm run build

# Install serve to serve the production build
RUN npm install -g serve

# Command to run the app
CMD ["serve", "-s", "build"]

# Expose port 3000
EXPOSE 3000
