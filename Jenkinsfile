pipeline {
    agent { label 'cegbu-lon-91' } 
    stages {
        stage('Checkout') {
            steps {
                // Pull latest code from Git
                git branch: 'main', url: 'https://oci.private.devops.scmservice.us-phoenix-1.oci.oracleiaas.com/namespaces/axuxirvibvvo/projects/GBUC/repositories/nextgen_cic_automation'
            }
        }
        stage('Build Podman Image') {
            steps {
                sh 'podman build -t playwright-python .'
            }
        }
        stage('Run Playwright Tests') {
            steps {
                sh 'podman run --rm --ipc=host playwright-python'
            }
        }
    }
}
