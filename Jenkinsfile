pipeline {
    agent any
    
    environment {
        DOCKER_BUILDKIT = '1'
        DOCKERHUB_USER = 'rhemisingh26'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo 'Setting up Python environment...'
                sh '''
                    python3 -m venv venv || true
                    . venv/bin/activate
                    pip install --upgrade pip
                '''
            }
        }
        
        stage('Lint & Tests') {
            steps {
                echo 'Running linting and tests...'
                sh '''
                    . venv/bin/activate
                    pip install -q pytest flake8 black || true
                    
                    # Run linting (continue on error)
                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                    
                    # Run tests if they exist
                    if [ -d "tests" ]; then
                        pytest -v tests/ || echo "Tests failed but continuing..."
                    else
                        echo "No tests directory found, skipping tests"
                    fi
                '''
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build API') {
                    steps {
                        echo 'Building API Docker image...'
                        sh '''
                            docker build \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                -t ${DOCKERHUB_USER}/mlops-api:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_USER}/mlops-api:latest \
                                -f Dockerfile.api \
                                .
                        '''
                    }
                }
                
                stage('Build UI') {
                    steps {
                        echo 'Building UI Docker image...'
                        sh '''
                            docker build \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                -t ${DOCKERHUB_USER}/mlops-ui:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_USER}/mlops-ui:latest \
                                -f Dockerfile.ui \
                                .
                        '''
                    }
                }
                
                stage('Build Agent') {
                    steps {
                        echo 'Building Agent Docker image...'
                        sh '''
                            docker build \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                -t ${DOCKERHUB_USER}/mlops-agent:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_USER}/mlops-agent:latest \
                                -f Dockerfile.agent \
                                .
                        '''
                    }
                }
                
                stage('Build MLflow') {
                    steps {
                        echo 'Building MLflow Docker image...'
                        sh '''
                            docker build \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                -t ${DOCKERHUB_USER}/mlops-mlflow:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_USER}/mlops-mlflow:latest \
                                -f Dockerfile.mlflow \
                                .
                        '''
                    }
                }
                
                stage('Build Training') {
                    steps {
                        echo 'Building Training Docker image...'
                        sh '''
                            docker build \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                -t ${DOCKERHUB_USER}/mlops-training:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_USER}/mlops-training:latest \
                                -f Dockerfile.training \
                                .
                        '''
                    }
                }
            }
        }
        
        stage('Push Docker Images') {
            steps {
                echo 'Logging in to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', 
                                                  usernameVariable: 'DOCKER_USER', 
                                                  passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        
                        echo "Pushing images to Docker Hub..."
                        docker push ${DOCKERHUB_USER}/mlops-api:${BUILD_NUMBER}
                        docker push ${DOCKERHUB_USER}/mlops-api:latest
                        
                        docker push ${DOCKERHUB_USER}/mlops-ui:${BUILD_NUMBER}
                        docker push ${DOCKERHUB_USER}/mlops-ui:latest
                        
                        docker push ${DOCKERHUB_USER}/mlops-agent:${BUILD_NUMBER}
                        docker push ${DOCKERHUB_USER}/mlops-agent:latest
                        
                        docker push ${DOCKERHUB_USER}/mlops-mlflow:${BUILD_NUMBER}
                        docker push ${DOCKERHUB_USER}/mlops-mlflow:latest
                        
                        docker push ${DOCKERHUB_USER}/mlops-training:${BUILD_NUMBER}
                        docker push ${DOCKERHUB_USER}/mlops-training:latest
                        
                        docker logout
                    '''
                }
            }
        }
        
        stage('Trigger Streamlit Deploy') {
            steps {
                echo 'Streamlit Cloud will auto-deploy from main branch'
                echo "Build ${BUILD_NUMBER} completed successfully!"
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo "Docker images pushed with tags: ${BUILD_NUMBER} and latest"
            echo "View images at: https://hub.docker.com/u/${DOCKERHUB_USER}"
        }
        failure {
            echo '❌ Pipeline failed!'
        }
        always {
            echo 'Cleaning up...'
        }
    }
}
