
pipeline {
    agent any

    stages {
        stage('Check Python and Docker') {
            steps {
                bat '''
                    @echo off
                    echo ===== PYTHON =====
                    "C:\\Users\\rekha\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe" --version

                    echo ===== DOCKER =====
                    "C:\\Users\\rekha\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" --version
                    "C:\\Users\\rekha\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" info
                '''
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
                    "C:\\Users\\rekha\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" ps
                    curl.exe -f http://localhost:5000
                '''
            }
        }
    }
}
