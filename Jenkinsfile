```groovy
pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Syntax Check') {
            steps {
                bat '''
                    @echo off
                    setlocal

                    echo Checking Python 3.11...

                    py -3.11 --version
                    if errorlevel 1 (
                        echo ERROR: Python 3.11 is unavailable to Jenkins.
                        exit /b 1
                    )

                    py -3.11 -m pip --version
                    if errorlevel 1 exit /b 1

                    echo Installing requirements...
                    py -3.11 -m pip install -r requirements.txt
                    if errorlevel 1 exit /b 1

                    echo Checking Python syntax...
                    py -3.11 -c "import pathlib; files=[p for p in pathlib.Path('.').rglob('*.py') if '.venv' not in p.parts and 'venv' not in p.parts]; print('Checking', len(files), 'Python files'); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('Syntax check passed')"
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Docker Smoke Test') {
            steps {
                bat '''
                    @echo off
                    setlocal

                    set "DOCKER=C:\\Users\\rekha\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    if not exist "%DOCKER%" (
                        echo ERROR: Docker executable not found.
                        exit /b 1
                    )

                    echo Checking Docker client...
                    "%DOCKER%" --version
                    if errorlevel 1 exit /b 1

                    echo Checking Docker engine access...
                    "%DOCKER%" info
                    if errorlevel 1 (
                        echo ERROR: Jenkins cannot access the Docker engine.
                        exit /b 1
                    )

                    echo Running smoke test...
                    "%DOCKER%" run --rm hello-world
                    if errorlevel 1 exit /b 1

                    echo Docker smoke test passed.
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished.'
        }
        success {
            echo 'SUCCESS: All stages passed.'
        }
        failure {
            echo 'FAILURE: Check the failed stage in Console Output.'
        }
    }
}
```
