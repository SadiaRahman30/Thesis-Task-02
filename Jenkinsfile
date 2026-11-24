pipeline {
    agent any

    environment {
        AWS_REGION     = 'us-east-1'
        AWS_ACCOUNT_ID = credentials('AWS_ACCOUNT_ID')
        IMAGE_NAME     = 'ml-model-app'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        ECR_REPO       = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}"
        ECS_CLUSTER    = 'ml-cluster'
        ECS_SERVICE    = 'ml-service'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Test & Lint') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    flake8 app.py train.py --count --max-line-length=127 --statistics || true
                    pytest tests/ || python3 -m unittest discover tests/
                '''
            }
        }

        stage('Security Scan (Trivy Filesystem)') {
            steps {
                sh '''
                    if command -v trivy &> /dev/null; then
                        trivy fs --exit-code 0 --severity HIGH,CRITICAL .
                    fi
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${ECR_REPO}:${IMAGE_TAG} -t ${ECR_REPO}:latest ."
            }
        }

        stage('Security Scan (Trivy Image)') {
            steps {
                sh '''
                    if command -v trivy &> /dev/null; then
                        trivy image --exit-code 0 --severity HIGH,CRITICAL ${ECR_REPO}:${IMAGE_TAG}
                    fi
                '''
            }
        }

        stage('Push to AWS ECR') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-credentials'
                ]]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                        docker push ${ECR_REPO}:${IMAGE_TAG}
                        docker push ${ECR_REPO}:latest
                    """
                }
            }
        }

        stage('Deploy to AWS ECS') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-credentials'
                ]]) {
                    sh """
                        aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --force-new-deployment --region ${AWS_REGION}
                    """
                }
            }
        }
    }

    post {
        always {
            sh 'rm -rf venv'
        }
    }
}
