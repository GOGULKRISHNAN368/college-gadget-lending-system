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

                    set "PYTHON_CMD="

                    py -3.11 --version >nul 2>&1
                    if not errorlevel 1 (
                        set "PYTHON_CMD=py -3.11"
                    )

                    if not defined PYTHON_CMD (
                        if exist "C:\\Users\\rekha\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe" (
                            set "PYTHON_CMD=C:\\Users\\rekha\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe"
                        )
                    )

                    if not defined PYTHON_CMD (
                        echo ERROR: Python 3.11 was not found.
                        exit /b 1
                    )

                    %PYTHON_CMD% --version
                    %PYTHON_CMD% -m pip --version

                    echo Installing project dependencies...

                    %PYTHON_CMD% -m pip install -r requirements.txt
                    if errorlevel 1 exit /b 1

                    echo Checking Python syntax...

                    %PYTHON_CMD% -c "import pathlib, sys; files=list(pathlib.Path('.').rglob('*.py')); files=[f for f in files if '.venv' not in f.parts and 'venv' not in f.parts and 'site-packages' not in f.parts]; print('Python files found:', len(files)); [compile(f.read_text(encoding='utf-8'), str(f), 'exec') for f in files]; print('Syntax check passed.')"
                    if errorlevel 1 exit /b 1

                    echo Build and syntax check completed successfully.
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
                        set "DOCKER=docker"
                    )

                    echo Checking Docker...

                    "%DOCKER%" --version
                    if errorlevel 1 (
                        echo ERROR: Docker is not accessible to Jenkins.
                        exit /b 1
                    )

                    "%DOCKER%" info
                    if errorlevel 1 (
                        echo ERROR: Docker Desktop engine is not running or accessible.
                        exit /b 1
                    )

                    echo Pulling a small test image...

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
            echo 'SUCCESS: All pipeline stages passed.'
        }

        failure {
            echo 'FAILURE: Check the console output for the failed stage.'
        }
    }
}
```
