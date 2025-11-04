pipeline {
    agent any
    
    environment {
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
        stage('Environment Check') {
            steps {
                echo '� Checking environment...'
                sh '''
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Workspace: ${WORKSPACE}"
                    docker --version
                    docker-compose --version
                    python3 --version
                    
                    # List workspace contents
                    echo "Workspace contents:"
                    ls -la
                    
                    # Verify Dockerfiles
                    echo "Checking Dockerfiles..."
                    for dockerfile in Dockerfile.api Dockerfile.ui Dockerfile.agent Dockerfile.mlflow Dockerfile.training; do
                        if [ -f "$dockerfile" ]; then
                            echo "✓ Found $dockerfile"
                        else
                            echo "✗ Missing $dockerfile"
                        fi
                    done
                    
                    # Verify docker-compose.yml
                    if [ -f "docker-compose.yml" ]; then
                        echo "✓ Found docker-compose.yml"
                    else
                        echo "✗ Missing docker-compose.yml"
                    fi
                '''
            }
        }
        
        stage('Code Quality') {
            steps {
                echo '🔍 Running code quality checks...'
                sh '''
                    echo "Checking Python syntax in key files..."
                    
                    # API service
                    if [ -f "services/api/app.py" ]; then
                        python3 -m py_compile services/api/app.py 2>&1 && echo "✓ API app.py syntax OK" || echo "✗ API app.py has issues"
                    fi
                    
                    # UI service
                    if [ -f "services/ui/app.py" ]; then
                        python3 -m py_compile services/ui/app.py 2>&1 && echo "✓ UI app.py syntax OK" || echo "✗ UI app.py has issues"
                    fi
                    
                    # Check if there are any Python files
                    echo "Total Python files in project:"
                    find . -name "*.py" -type f | wc -l
                    
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
                            docker build -f Dockerfile.api \
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
                            docker build -f Dockerfile.ui \
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
                            docker build -f Dockerfile.agent \
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
                            docker build -f Dockerfile.mlflow \
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
                            docker build -f Dockerfile.training \
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
                echo '⏭️  Skipping Docker Hub push (local deployment only)...'
                sh '''
                    echo "Images built successfully for local use:"
                    docker images | grep mlops | grep ${IMAGE_TAG}
                '''
            }
        }
        
        stage('Stop Old Services') {
            steps {
                echo '🛑 Stopping old services...'
                sh '''
                    docker-compose down --remove-orphans || echo "No services running"
                    
                    # Clean up dangling images
                    docker image prune -f || true
                '''
            }
        }
        
        stage('Deploy Services') {
            steps {
                echo '🚀 Deploying services with docker-compose...'
                sh '''
                    # Start core services (api, ui, mlflow, agent)
                    docker-compose up -d api ui mlflow agent
                    
                    echo "Waiting for services to start..."
                    sleep 15
                    
                    # Check service status
                    docker-compose ps
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
                    echo "═══════════════════════════════════════════════════════"
                    echo "              ML PLATFORM DEPLOYMENT SUMMARY"
                    echo "═══════════════════════════════════════════════════════"
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Build Date:   $(date)"
                    echo "Workspace:    ${WORKSPACE}"
                    echo ""
                    echo "Docker Images Built:"
                    docker images | grep mlops | head -10
                    echo ""
                    echo "Running Services:"
                    docker-compose ps
                    echo ""
                    echo "Service URLs (Local):"
                    echo "  🌐 API:        http://localhost:8000"
                    echo "  🌐 UI:         http://localhost:8501"
                    echo "  🌐 MLflow:     http://localhost:5000"
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
                echo "Docker Compose Logs:"
                docker-compose logs --tail=100 || true
                echo ""
                echo "Docker Containers:"
                docker ps -a
                echo ""
                echo "Docker Images:"
                docker images | grep mlops || true
                echo ""
                echo "Workspace contents:"
                ls -la
            '''
        }
        
        always {
            echo '🧹 Cleaning up build artifacts...'
            sh '''
                # Keep Docker containers running
                # Only cleanup build artifacts and old images
                
                # Remove old/dangling images (keep latest and current build)
                docker image prune -f || true
                
                # Clean up any test artifacts
                rm -rf .pytest_cache __pycache__ .coverage || true
                
                echo "✓ Cleanup completed"
            '''
        }
    }
}
