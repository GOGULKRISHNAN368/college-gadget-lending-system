
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and syntax check') {
            steps {
                bat 'py -3 -m pip install -r requirements.txt'
                bat 'py -3 -m py_compile app.py'
            }
        }

        stage('Docker smoke test') {
            steps {
                bat 'docker build -t devapps-cat2:%BUILD_NUMBER% .'
                bat 'docker rm -f devapps-ci-test'
                bat 'docker run -d --name devapps-ci-test -p 5055:5000 -e DATABASE_PATH=/tmp/devapps-ci.db -e ADMIN_EMAIL=ci-admin@example.test -e ADMIN_PASSWORD=CiAdmin123! devapps-cat2:%BUILD_NUMBER%'
                bat 'powershell -NoProfile -Command "$ok = $false; for ($i=0; $i -lt 20; $i++) { try { Invoke-WebRequest -Uri http://localhost:5055/health -UseBasicParsing -TimeoutSec 2 | Out-Null; $ok = $true; break } catch { Start-Sleep -Seconds 2 } }; if (-not $ok) { exit 1 }"'
                bat 'curl.exe -f http://localhost:5055/health'
                bat 'docker rm -f devapps-ci-test'
            }
        }
    }

    post {
        always {
            echo 'Check stage logs for build and smoke-test results.'
        }
    }
}
