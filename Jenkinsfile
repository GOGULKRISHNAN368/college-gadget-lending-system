
pipeline {
    agent any

    stages {
        stage('Check Python and Docker') {
            steps {
                bat '''
                    @echo off
                    echo ===== PYTHON =====
                    py -3.11 --version

                    echo ===== DOCKER =====
                    docker --version
                    docker info
                '''
            }
        }

        stage('Checkout Project') {
            steps {
                echo 'Project source is checked out by Jenkins from SCM.'
            }
        }

        stage('Deploy Using Ansible') {
            steps {
                bat '''
                    @echo off
                    wsl -d Ubuntu -- bash -lc "cd '/mnt/d/devops cat/devapps-cat2' && ansible-playbook ansible-playbook.yml"
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                bat '''
                    @echo off
                    docker ps
                    curl.exe -f http://localhost:5000
                '''
            }
        }
    }
}
