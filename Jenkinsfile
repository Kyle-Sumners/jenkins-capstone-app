pipeline {
  agent any

  environment {
    IMAGE_REPO = "quay.io/ksumners66/jenkins-capstone"
    IMAGE_TAG = "${BRANCH_NAME}-${BUILD_NUMBER}"
    GIT_SHA = "${GIT_COMMIT.take(7)}"
    NOTIFY_EMAIL = credentials('notify-email')
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
      when { branch 'main' }
      steps {
        sh "docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -t ${IMAGE_REPO}:${GIT_SHA} -t ${IMAGE_REPO}:latest ."
      }
    }

    stage("Docker push") {
      when { branch 'main' }
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
      when { branch 'main' }
      steps {
        sh '''
          docker pull $IMAGE_REPO:$IMAGE_TAG
          docker rm -f capstone-app
          docker run -d -p 5000:5000 --name capstone-app -e VERSION=$IMAGE_TAG $IMAGE_REPO:$IMAGE_TAG
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
              .find { it ==~ /main-\d+/ } ?: 'stable'
              
            sh """
              docker rm -f capstone-app
              docker run -d -p 5000:5000 --name capstone-app -e VERSION=${stableVersion} ${IMAGE_REPO}:stable
              curl --retry 3 --retry-delay 2 --retry-all-errors --fail docker:5000/health
            """
          }
        }
      }
    }

    stage("Approve as stable") {
      when { branch 'main' }
      steps {
        timeout(time: 15, unit: 'MINUTES') {
          input message: "Build ${BUILD_NUMBER} is deployed and healthy. Mark it as the stable release?", ok: "Mark stable"
        }
      }
    }

    stage("Promote") {
      when { branch 'main' }
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

  post {
    success {
      emailext to: NOTIFY_EMAIL,
        subject: "SUCCESS: ${JOB_NAME} #${BUILD_NUMBER} deployed",
        body: """Build ${BUILD_NUMBER} passed all stages and is deployed.

Image: ${IMAGE_REPO}:${IMAGE_TAG}
Commit: ${GIT_SHA}
Marked stable: yes

Details: ${BUILD_URL}"""
    }
    failure {
      emailext to: NOTIFY_EMAIL,
        subject: "FAILED: ${JOB_NAME} #${BUILD_NUMBER}",
        body: """Build ${BUILD_NUMBER} failed.

Commit: ${GIT_SHA}
If the failure occurred during deployment, an automatic rollback to the last stable version was attempted.

Details: ${BUILD_URL}"""
    }

    aborted {
      emailext to: NOTIFY_EMAIL,
        subject: "ABORTED: ${JOB_NAME} #${BUILD_NUMBER}",
        body: """Build ${BUILD_NUMBER} was aborted.

Commit: ${GIT_SHA}
Build ${BUILD_NUMBER} deployed successfully but was not promoted to stable — the approval either timed out or was declined.

Details: ${BUILD_URL}"""
    }
  }
}