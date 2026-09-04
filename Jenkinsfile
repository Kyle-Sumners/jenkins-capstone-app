pipeline {
  agent any

  stages {
    stage("Test") {
      agent {
        docker {
          image 'python:3.14.7-slim'
          reuseNode true
        }
      }

      steps {
        sh '''
          pip install -r requirements-dev.txt
          mkdir -p test-results
          pytest --junitxml=test-results/pytest-report.xml
        '''
      }

      post {
        always {
          junit 'test-results/pytest-report.xml'
        }
      }
    }
  }
}