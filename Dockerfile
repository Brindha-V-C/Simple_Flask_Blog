# Step 1: Start from a lightweight Python base image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file first for better caching
COPY requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy your entire application into the container
COPY . .

# Step 6: Expose the port that Flask runs on (default is 5000)
EXPOSE 5000

# Step 7: Define the command to run your app
CMD ["python", "app.py"]