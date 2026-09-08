pipeline {
  agent any

  environment {
    IMAGE_REPO = "quay.io/ksumners66/jenkins-capstone"
    IMAGE_TAG = "${BUILD_NUMBER}"
    GIT_SHA = "${GIT_COMMIT.take(7)}"
  }

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
          python -m venv .venv
          .venv/bin/pip install -r requirements-dev.txt
          mkdir -p test-results
          .venv/bin/pytest --junitxml=test-results/pytest-report.xml
        '''
      }

      post {
        always {
          junit 'test-results/pytest-report.xml'
        }
      }
    }

    stage("Docker build") {
      steps {
        sh "docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -t ${IMAGE_REPO}:${GIT_SHA} -t ${IMAGE_REPO}:latest ."
      }
    }

    stage("Docker push") {
      steps {
        withCredentials([usernamePassword(credentialsId: 'Quay-robot', passwordVariable: 'QUAY_PW', usernameVariable: 'QUAY_USER')]) {
          sh '''
            echo "$QUAY_PW" | docker login quay.io -u "$QUAY_USER" --password-stdin
            docker push $IMAGE_REPO:$IMAGE_TAG
            docker push $IMAGE_REPO:$GIT_SHA
            docker push $IMAGE_REPO:latest
            docker logout quay.io
          '''
        }
      }
    }

    stage("Deploy") {
      steps {
        sh '''
          docker pull $IMAGE_REPO:$IMAGE_TAG
          docker rm -f capstone-app
          docker run -d -p 5000:5000 --name capstone-app -e VERSION=$IMAGE_TAG -e DB_STATUS=down $IMAGE_REPO:$IMAGE_TAG
          curl --retry 3 --retry-delay 2 --retry-all-errors --fail docker:5000/health
        '''
      }

      post {
        failure {
          script {
            sh 'docker pull $IMAGE_REPO:stable'
            def tags = sh(
              script: "docker image inspect --format '{{join .RepoTags \",\"}}' ${IMAGE_REPO}:stable",
              returnStdout: true
            ).trim()

            def stableVersion = tags.split(',')
              .collect { it.tokenize(':').last() }
              .find { it ==~ /\d+/ } ?: 'stable'
              
            sh """
              docker rm -f capstone-app
              docker run -d -p 5000:5000 --name capstone-app -e VERSION=${stableVersion} ${IMAGE_REPO}:stable
              curl --retry 3 --retry-delay 2 --retry-all-errors --fail docker:5000/health
            """
          }
        }
      }
    }

    stage("Promote") {
      steps {
        withCredentials([usernamePassword(credentialsId: 'Quay-robot', passwordVariable: 'QUAY_PW', usernameVariable: 'QUAY_USER')]) {
          sh '''
            echo "$QUAY_PW" | docker login quay.io -u "$QUAY_USER" --password-stdin
            docker tag $IMAGE_REPO:$IMAGE_TAG $IMAGE_REPO:stable
            docker push $IMAGE_REPO:stable
            docker logout quay.io
          '''
        }
      }
    }
  }
}