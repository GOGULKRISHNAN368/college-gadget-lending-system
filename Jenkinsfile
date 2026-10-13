pipeline {
    agent any

    stages {
        stage('Check Python and Docker') {
            steps {
                bat '''
                    @echo off
                    setlocal

                    echo ===== PYTHON =====

                    set "PYTHON=C:\\Users\\rekha\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe"

                    if exist "%PYTHON%" (
                        "%PYTHON%" --version
                        "%PYTHON%" -m pip --version
                    ) else (
                        echo Python executable not accessible at this path.
                        exit /b 1
                    )

                    echo ===== DOCKER =====

                    set "DOCKER=C:\\Users\\rekha\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    if exist "%DOCKER%" (
                        "%DOCKER%" --version
                        "%DOCKER%" info
                    ) else (
                        echo Docker executable not accessible at this path.
                        exit /b 1
                    )
                '''
            }
        }
    }
}
