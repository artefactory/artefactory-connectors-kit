include .env

define build_docker_image
	docker image build --rm -t $(1):$(2) -f $(3) .
	docker tag $(1):$(2) $(1):latest
endef

define publish_docker_image
	docker tag $(1):$(2) ${DOCKER_REGISTRY}/${PROJECT_ID}/$(1):$(2)
	docker push ${DOCKER_REGISTRY}/${PROJECT_ID}/$(1):$(2)
endef

.PHONY: configure_docker_auth
configure_docker_auth:
	gcloud --project $(PROJECT_ID) auth configure-docker

.PHONY: build_base_image
build_base_image:
	$(call build_docker_image,${DOCKER_IMAGE},${DOCKER_TAG},Dockerfile)

.PHONY: publish_base_image
publish_base_image: build_base_image configure_docker_auth
	$(call publish_docker_image,${DOCKER_IMAGE},${DOCKER_TAG})
	$(call publish_docker_image,${DOCKER_IMAGE},latest)
