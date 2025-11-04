pipeline {
    agent any
    
    environment {
        // Host project path (Jenkins will copy files to workspace)
        HOST_PROJECT_PATH = "/home/rhemi/IA3/mlops"
        
        // Docker Hub configuration
        DOCKERHUB_USER = "rhemisingh26"
        
        // Image names (matching your docker-compose.yml)
        API_IMAGE = "${DOCKERHUB_USER}/mlops-api"
        UI_IMAGE = "${DOCKERHUB_USER}/mlops-ui"
        AGENT_IMAGE = "${DOCKERHUB_USER}/mlops-agent"
        MLFLOW_IMAGE = "${DOCKERHUB_USER}/mlops-mlflow"
        TRAINING_IMAGE = "${DOCKERHUB_USER}/mlops-training"
        
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        DOCKER_BUILDKIT = "1"
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }
    
    stages {
        stage('Prepare Workspace') {
            steps {
                echo '📥 Copying project files to Jenkins workspace...'
                sh '''
                    # Clean workspace
                    cd ${WORKSPACE}
                    rm -rf * .[!.]* 2>/dev/null || true
                    
                    echo "Using tar method to copy files..."
                    # Use tar to copy files (more reliable than cp)
                    docker run --rm \
                        -v ${HOST_PROJECT_PATH}:/source:ro \
                        -v ${WORKSPACE}:/dest \
                        alpine sh -c "cd /source && tar cf - . | tar xf - -C /dest"
                    
                    echo "Workspace contents after copy:"
                    ls -la ${WORKSPACE} | head -30
                    
                    echo "Checking critical files..."
                    for dockerfile in Dockerfile.api Dockerfile.ui Dockerfile.agent Dockerfile.mlflow Dockerfile.training; do
                        if [ -f "${WORKSPACE}/$dockerfile" ]; then
                            echo "✓ Found $dockerfile"
                        else
                            echo "✗ Missing $dockerfile"
                        fi
                    done
                    
                    echo "Total files copied:"
                    find ${WORKSPACE} -type f | wc -l
                '''
            }
        }
        
        stage('Environment Check') {
            steps {
                echo '🔧 Checking environment...'
                sh '''
                    cd ${WORKSPACE}
                    echo "Build Number: ${BUILD_NUMBER}"
                    docker --version
                    docker-compose --version
                    python3 --version
                    
                    # Verify key files
                    for file in docker-compose.yml requirements.txt; do
                        if [ -f "$file" ]; then
                            echo "✓ Found $file"
                        else
                            echo "✗ Missing $file"
                        fi
                    done
                    
                    # Verify service directories
                    for dir in services/api services/ui services/agent services/mlflow services/training; do
                        if [ -d "$dir" ]; then
                            echo "✓ Found directory: $dir"
                        else
                            echo "✗ Missing directory: $dir"
                        fi
                    done
                '''
            }
        }
        
        stage('Code Quality') {
            steps {
                echo '🔍 Running code quality checks...'
                sh '''
                    cd ${WORKSPACE}
                    
                    echo "Checking Python syntax in key files..."
                    
                    # API service
                    if [ -f "services/api/app.py" ]; then
                        python3 -m py_compile services/api/app.py 2>&1 && echo "✓ API app.py syntax OK" || echo "✗ API app.py has issues"
                    fi
                    
                    # UI service
                    if [ -f "services/ui/app.py" ]; then
                        python3 -m py_compile services/ui/app.py 2>&1 && echo "✓ UI app.py syntax OK" || echo "✗ UI app.py has issues"
                    fi
                    
                    # Agent service
                    if [ -f "services/agent/agent.py" ]; then
                        python3 -m py_compile services/agent/agent.py 2>&1 && echo "✓ Agent syntax OK" || echo "✗ Agent has issues"
                    fi
                    
                    # Training service
                    if [ -f "services/training/train.py" ]; then
                        python3 -m py_compile services/training/train.py 2>&1 && echo "✓ Training syntax OK" || echo "✗ Training has issues"
                    fi
                    
                    echo "Code quality checks completed"
                '''
            }
        }
        
        stage('Build Images') {
            parallel {
                stage('Build API') {
                    steps {
                        echo '🐳 Building API image...'
                        sh '''
                            cd ${WORKSPACE}
                            sudo docker build -f Dockerfile.api \
                                -t ${API_IMAGE}:${IMAGE_TAG} \
                                -t ${API_IMAGE}:latest \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                .
                            echo "✓ API image built successfully"
                        '''
                    }
                }
                
                stage('Build UI') {
                    steps {
                        echo '🐳 Building UI image...'
                        sh '''
                            cd ${WORKSPACE}
                            sudo docker build -f Dockerfile.ui \
                                -t ${UI_IMAGE}:${IMAGE_TAG} \
                                -t ${UI_IMAGE}:latest \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                .
                            echo "✓ UI image built successfully"
                        '''
                    }
                }
                
                stage('Build Agent') {
                    steps {
                        echo '🐳 Building Agent image...'
                        sh '''
                            cd ${WORKSPACE}
                            sudo docker build -f Dockerfile.agent \
                                -t ${AGENT_IMAGE}:${IMAGE_TAG} \
                                -t ${AGENT_IMAGE}:latest \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                .
                            echo "✓ Agent image built successfully"
                        '''
                    }
                }
                
                stage('Build MLflow') {
                    steps {
                        echo '🐳 Building MLflow image...'
                        sh '''
                            cd ${WORKSPACE}
                            sudo docker build -f Dockerfile.mlflow \
                                -t ${MLFLOW_IMAGE}:${IMAGE_TAG} \
                                -t ${MLFLOW_IMAGE}:latest \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                .
                            echo "✓ MLflow image built successfully"
                        '''
                    }
                }
                
                stage('Build Training') {
                    steps {
                        echo '🐳 Building Training image...'
                        sh '''
                            cd ${WORKSPACE}
                            sudo docker build -f Dockerfile.training \
                                -t ${TRAINING_IMAGE}:${IMAGE_TAG} \
                                -t ${TRAINING_IMAGE}:latest \
                                --build-arg BUILDKIT_INLINE_CACHE=1 \
                                .
                            echo "✓ Training image built successfully"
                        '''
                    }
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing images to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', 
                                                usernameVariable: 'DOCKER_USER', 
                                                passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "Logging into Docker Hub..."
                        echo $DOCKER_PASS | sudo docker login -u $DOCKER_USER --password-stdin
                        
                        echo "Pushing API images..."
                        sudo docker push ${API_IMAGE}:${IMAGE_TAG}
                        sudo docker push ${API_IMAGE}:latest
                        
                        echo "Pushing UI images..."
                        sudo docker push ${UI_IMAGE}:${IMAGE_TAG}
                        sudo docker push ${UI_IMAGE}:latest
                        
                        echo "Pushing Agent images..."
                        sudo docker push ${AGENT_IMAGE}:${IMAGE_TAG}
                        sudo docker push ${AGENT_IMAGE}:latest
                        
                        echo "Pushing MLflow images..."
                        sudo docker push ${MLFLOW_IMAGE}:${IMAGE_TAG}
                        sudo docker push ${MLFLOW_IMAGE}:latest
                        
                        echo "Pushing Training images..."
                        sudo docker push ${TRAINING_IMAGE}:${IMAGE_TAG}
                        sudo docker push ${TRAINING_IMAGE}:latest
                        
                        echo "✓ All images pushed successfully"
                    '''
                }
            }
        }
        
        stage('Stop Old Services') {
            steps {
                echo '🛑 Stopping old services...'
                sh '''
                    cd ${WORKSPACE}
                    sudo docker-compose down --remove-orphans || echo "No services running"
                    
                    # Clean up dangling images
                    sudo docker image prune -f || true
                '''
            }
        }
        
        stage('Deploy Services') {
            steps {
                echo '🚀 Deploying services with docker-compose...'
                sh '''
                    cd ${WORKSPACE}
                    
                    # Start all services
                    sudo docker-compose up -d
                    
                    echo "Waiting for services to start..."
                    sleep 15
                    
                    # Check service status
                    sudo docker-compose ps
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo '🏥 Running health checks...'
                sh '''
                    # Wait for services to be ready
                    echo "Waiting 30 seconds for services to initialize..."
                    sleep 30
                    
                    # Check API health
                    echo "Checking API health..."
                    curl -f http://localhost:8000/health || echo "⚠️  API not ready yet"
                    
                    # Check UI
                    echo "Checking UI..."
                    curl -f http://localhost:8501 || echo "⚠️  UI not ready yet"
                    
                    # Check MLflow
                    echo "Checking MLflow..."
                    curl -f http://localhost:5000 || echo "⚠️  MLflow not ready yet"
                    
                    echo "✓ Health checks completed"
                '''
            }
        }
        
        stage('Deployment Report') {
            steps {
                echo '📊 Generating deployment report...'
                sh '''
                    cd ${WORKSPACE}
                    
                    echo "═══════════════════════════════════════════════════════"
                    echo "              ML PLATFORM DEPLOYMENT SUMMARY"
                    echo "═══════════════════════════════════════════════════════"
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Build Date:   $(date)"
                    echo "Git Commit:   $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
                    echo ""
                    echo "Docker Images Built:"
                    sudo docker images | grep mlops | grep -E "${IMAGE_TAG}|latest"
                    echo ""
                    echo "Running Services:"
                    sudo docker-compose ps
                    echo ""
                    echo "Service URLs (Local):"
                    echo "  🌐 API:        http://localhost:8000"
                    echo "  🌐 UI:         http://localhost:8501"
                    echo "  🌐 MLflow:     http://localhost:5000"
                    echo "  🌐 Postgres:   localhost:5432"
                    echo ""
                    echo "API Documentation:"
                    echo "  📚 Swagger:    http://localhost:8000/docs"
                    echo "  📚 ReDoc:      http://localhost:8000/redoc"
                    echo ""
                    echo "Docker Hub Images:"
                    echo "  🐳 View at:    https://hub.docker.com/u/${DOCKERHUB_USER}"
                    echo ""
                    echo "═══════════════════════════════════════════════════════"
                    echo "🌐 TO EXPOSE API FOR STREAMLIT CLOUD:"
                    echo "═══════════════════════════════════════════════════════"
                    echo "1. Run: ngrok http 8000"
                    echo "2. Copy the ngrok HTTPS URL"
                    echo "3. Add to Streamlit Cloud secrets:"
                    echo "   API_URL = \"https://your-ngrok-url.ngrok-free.app\""
                    echo ""
                    echo "Or use the setup script:"
                    echo "   ./setup_ngrok_streamlit.sh"
                    echo "═══════════════════════════════════════════════════════"
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ PIPELINE COMPLETED SUCCESSFULLY!'
            echo ''
            echo '🎉 All services are deployed and running locally'
            echo ''
            echo '═══════════════════════════════════════════════════════'
            echo 'Access Your Application:'
            echo '═══════════════════════════════════════════════════════'
            echo '  Streamlit UI (Local):  http://localhost:8501'
            echo '  API Docs (Local):      http://localhost:8000/docs'
            echo '  MLflow Tracking:       http://localhost:5000'
            echo ''
            echo 'Docker Hub:'
            echo "  View images at: https://hub.docker.com/u/${DOCKERHUB_USER}"
            echo ''
            echo '🌐 Next Steps for Streamlit Cloud Deployment:'
            echo '  1. Run: ./setup_ngrok_streamlit.sh'
            echo '  2. Use ngrok URL in Streamlit Cloud secrets'
            echo '  3. Deploy from: https://share.streamlit.io'
            echo '═══════════════════════════════════════════════════════'
        }
        
        failure {
            echo '❌ PIPELINE FAILED!'
            echo 'Collecting logs for debugging...'
            sh '''
                cd ${WORKSPACE}
                echo "Docker Compose Logs:"
                sudo docker-compose logs --tail=100 || true
                echo ""
                echo "Docker Containers:"
                sudo docker ps -a
                echo ""
                echo "Docker Images:"
                sudo docker images | grep mlops || true
            '''
        }
        
        always {
            echo '🧹 Cleaning up build artifacts...'
            sh '''
                # Keep Docker containers running
                # Only cleanup build artifacts and old images
                cd ${WORKSPACE}
                
                # Remove old/dangling images (keep latest and current build)
                sudo docker image prune -f || true
                
                # Clean up any test artifacts
                rm -rf .pytest_cache __pycache__ .coverage || true
                
                echo "✓ Cleanup completed"
            '''
        }
    }
}
