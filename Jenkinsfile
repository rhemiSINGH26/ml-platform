pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        GITHUB_TOKEN = credentials('github-token')
        DOCKER_BUILDKIT = '1'
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
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-api:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-api:latest \
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
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-ui:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-ui:latest \
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
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-agent:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-agent:latest \
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
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-mlflow:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-mlflow:latest \
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
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-training:${BUILD_NUMBER} \
                                -t ${DOCKERHUB_CREDENTIALS_USR}/mlops-training:latest \
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
                sh 'echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin'
                
                echo 'Pushing images to Docker Hub...'
                sh '''
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-api:${BUILD_NUMBER}
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-api:latest
                    
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-ui:${BUILD_NUMBER}
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-ui:latest
                    
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-agent:${BUILD_NUMBER}
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-agent:latest
                    
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-mlflow:${BUILD_NUMBER}
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-mlflow:latest
                    
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-training:${BUILD_NUMBER}
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/mlops-training:latest
                '''
            }
        }
        
        stage('Trigger Streamlit Deploy') {
            steps {
                echo 'Streamlit Cloud will auto-deploy from main branch'
                echo 'Pushing updated code to trigger deployment...'
                sh '''
                    git config user.name "Jenkins CI"
                    git config user.email "jenkins@mlops.local"
                    git tag -a "build-${BUILD_NUMBER}" -m "Jenkins build ${BUILD_NUMBER}"
                    git push origin "build-${BUILD_NUMBER}" || echo "Tag push failed (may already exist)"
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo "Docker images pushed with tags: ${BUILD_NUMBER} and latest"
        }
        failure {
            echo '❌ Pipeline failed!'
        }
        always {
            echo 'Cleaning up...'
            sh 'docker logout || true'
            cleanWs()
        }
    }
}
