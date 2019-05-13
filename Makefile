ifndef ENV
	environment = dev
else
	environment = ${ENV}
endif

include environments/$(environment)

.PHONY: k8s_setup
init: k8s_setup
	gcloud --project ${PROJECT_ID} auth configure-docker

.PHONY: upgrade_crons
upgrade_crons:
	helm upgrade dash-finance ./helm

.PHONY: install_crons
install_crons: delete_crons
	helm install -n dash-finance ./helm

.PHONY: delete_crons
delete_crons:
	kubectl delete cronjob --all

.PHONY: deploy_docker
deploy_docker: docker_tag
	docker push ${DOCKER_REGISTRY}/${PROJECT_ID}/${DOCKER_IMAGE}:latest

.PHONY: docker_tag
docker_tag: docker_build
	docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${PROJECT_ID}/${DOCKER_IMAGE}:latest

.PHONY: docker_build
docker_build:
	docker build . --tag ${DOCKER_IMAGE} --build-arg ENV=$(environment)

.PHONY: k8s_setup
k8s_setup:
	gcloud container clusters get-credentials ${K8S_CLUSTER_NAME} \
		--zone ${K8S_ZONE} \
		--project ${PROJECT_ID}

.PHONY: k8s_secrets
k8s_secrets: k8s_setup
	kubectl create secret generic ingestion-secrets \
	--from-file ./data/secrets/sheets.json  \
	--from-file ./data/secrets/google_credentials.json \
	--from-file ./data/secrets/mysql.json \
	--from-file ./data/secrets/oracle.json

.PHONY: k8s_delete_secrets
k8s_delete_secrets:
	kubectl delete secret ingestion-secrets