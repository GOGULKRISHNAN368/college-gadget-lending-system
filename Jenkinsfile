pipeline {
  agent any
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build and syntax check') {
      steps {
        sh 'python3 -m pip install -r requirements.txt'
        sh 'python3 -m py_compile app.py'
      }
    }
    stage('Docker smoke test') {
      steps {
        sh '''
          docker build -t devapps-cat2:${BUILD_NUMBER} .
          docker rm -f devapps-ci-test || true
          docker run -d --name devapps-ci-test -p 5055:5000 -e DATABASE_PATH=/tmp/devapps-ci.db -e ADMIN_EMAIL=ci-admin@example.test -e ADMIN_PASSWORD=CiAdmin123! devapps-cat2:${BUILD_NUMBER}
          for i in $(seq 1 20); do curl -fsS http://localhost:5055/health && break || sleep 2; done
          curl -fsS http://localhost:5055/health
          docker rm -f devapps-ci-test
        '''
      }
    }
  }
  post { always { echo 'Check stage logs for build and smoke-test results.' } }
}
