pipeline {
    agent none

    stages {
        // -----------------------------------------------------------------
        // STAGE 1: Build & Test
        // -----------------------------------------------------------------
        stage('Build & Test') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    args '--user root --entrypoint=""'
                }
            }
            steps {
                checkout scm
                sh 'pip install -r requirements.txt'
                sh 'pip install flake8'
                sh 'flake8 .'
                echo 'Build & Test complete!'
            }
        }

        // -----------------------------------------------------------------
        // STAGE 2: Package & Push
        // -----------------------------------------------------------------
        stage('Package & Push') {
            agent {
                docker {
                    image 'docker:latest'
                    args '--user root --entrypoint="" -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                checkout scm
                script {
                    // --- UPDATE THIS LINE with your Docker Hub username ---
                    def imageName = "YOUR_DOCKERHUB_USERNAME/flask-blog:${env.BUILD_NUMBER}"
                    def appImage = docker.build(imageName, ".")

                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-creds') {
                        appImage.push()
                    }
                }
            }
        }
        
        // -----------------------------------------------------------------
        // STAGE 3: Deploy to Staging
        // -----------------------------------------------------------------
        stage('Deploy to Staging') {
            // Run this on any available agent that has SSH
            agent any
            
            steps {
                script {
                    def imageName = "YOUR_DOCKERHUB_USERNAME/flask-blog:${env.BUILD_NUMBER}"
                    def vm_ip = "YOUR_VM_PUBLIC_IP"
                    def vm_user = "azureuser"

                    // Use the sshagent wrapper to load the 'azure-vm-key' credentials
                    sshagent(credentials: ['azure-vm-key']) {
                        
                        echo "Connecting to ${vm_user}@${vm_ip}..."
                        
                        // Run the remote commands on the Azure VM
                        sh """
                            ssh -o StrictHostKeyChecking=no ${vm_user}@${vm_ip} '''
                                echo 'Connected to VM!'

                                echo 'Pulling the new image from Docker Hub...'
                                docker pull ${imageName}
                                
                                echo 'Stopping and removing the old container...'
                                docker stop flask-blog-app || true
                                docker rm flask-blog-app || true
                                
                                echo 'Starting the new container...'
                                docker run -d --name flask-blog-app -p 80:5000 ${imageName}
                                
                                echo 'Deployment complete!'
                            '''
                        """
                    }
                }
            }
        }
    }
}