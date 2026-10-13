pipeline {
    agent any

    stages {
        stage('Check Jenkins Environment') {
            steps {
                bat '''
                    @echo off
                    echo ===== SERVICE ENVIRONMENT =====
                    whoami

                    echo ===== PYTHON LAUNCHER =====
                    where py
                    py -3.11 --version

                    echo ===== DOCKER =====
                    where docker
                    docker --version
                    docker info
                '''
            }
        }
    }
}
