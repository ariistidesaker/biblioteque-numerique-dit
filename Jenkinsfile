pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(
            name: 'RUN_DOCKER_BUILD',
            defaultValue: true,
            description: 'Construire les images Docker (docker compose build)'
        )
        booleanParam(
            name: 'RUN_DVC_PIPELINE',
            defaultValue: false,
            description: 'Exécuter dvc repro (nécessite les données : dvc pull)'
        )
    }

    environment {
        PYTHON = 'python3'
        COMPOSE_PROJECT_NAME = 'bibliotheque-dit-ci'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Vérifications qualité') {
            parallel {
                stage('Frontend — lint & build') {
                    steps {
                        dir('frontend') {
                            sh 'npm ci'
                            sh 'npm run lint'
                            sh 'npm run build'
                        }
                    }
                }

                stage('Backend — compilation Python') {
                    steps {
                        sh '''
                            set -e
                            ${PYTHON} -m compileall -q backend
                        '''
                    }
                }

                stage('Backend — dépendances') {
                    steps {
                        sh '''
                            set -e
                            for service in livres utilisateurs emprunts recommandation; do
                                echo "=== ${service} ==="
                                ${PYTHON} -m pip install --quiet -r "backend/${service}/app/requirements.txt"
                            done
                            ${PYTHON} -m pip install --quiet scikit-learn pandas numpy joblib
                        '''
                    }
                }
            }
        }

        stage('Docker — build des images') {
            when {
                expression { return params.RUN_DOCKER_BUILD }
            }
            steps {
                sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.yml build --parallel'
            }
        }

        stage('Pipeline DVC (ML)') {
            when {
                expression { return params.RUN_DVC_PIPELINE }
            }
            steps {
                sh '''
                    set -e
                    ${PYTHON} -m pip install --quiet "dvc[gdrive]>=3.0"
                    dvc --version
                    dvc pull || echo "AVERTISSEMENT: dvc pull a échoué (remote non configuré ?)"
                    dvc repro
                    dvc metrics show
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.yml down -v --remove-orphans 2>/dev/null || true'
            cleanWs(cleanWhenNotBuilt: false, deleteDirs: true, disableDeferredWipeout: true)
        }
        success {
            echo 'Pipeline Jenkins terminé avec succès.'
        }
        failure {
            echo 'Pipeline Jenkins en échec — consultez les logs des stages en erreur.'
        }
    }
}
