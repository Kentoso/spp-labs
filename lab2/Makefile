project_id := labs-knu-ds
worker_count := 3
machine_type := n1-standard-1
zone := europe-north1-a
ip_file := leader_ip.txt
worker_env_file := worker.env

firewall:
	@if ! gcloud compute firewall-rules list --filter="name=allow-parcs-inbound" --format="value(name)" | grep -q "allow-parcs-inbound"; then \
		gcloud compute firewall-rules create allow-parcs-inbound \
			--direction=INGRESS \
			--priority=1000 \
			--network=default \
			--action=ALLOW \
			--rules=all \
			--source-ranges=0.0.0.0/0 \
			--target-tags=parcs-instance; \
	else \
		echo "Firewall rule 'allow-parcs-inbound' already exists. Skipping creation."; \
	fi


delete-firewall:
	gcloud compute firewall-rules delete allow-parcs-inbound --quiet

list-firewall:
	gcloud compute firewall-rules list --filter="name=allow-parcs-inbound"

leader: firewall
	@if gcloud compute instances list --filter="name=parcs-leader AND zone=$(zone)" --format="value(name)" | grep -q "parcs-leader"; then \
		echo "parcs-leader already exists. Skipping creation."; \
	else \
		gcloud compute instances create-with-container parcs-leader \
			--tags=parcs-instance \
			--container-image=registry.hub.docker.com/hummer12007/parcs-node \
			--container-env=PARCS_ARGS="master" \
			--provisioning-model=SPOT \
			--zone=$(zone) \
			--project=$(project_id) \
			--machine-type=$(machine_type); \
	fi
	@sleep 5
	@echo "PARCS_ARGS=worker $$(gcloud compute instances describe parcs-leader --zone=$(zone) --project=$(project_id) --format='get(networkInterfaces[0].networkIP)')" > $(worker_env_file)
	@echo "Worker env saved in $(worker_env_file): $$(cat $(worker_env_file))"

workers: leader firewall
	@if [ ! -f $(worker_env_file) ]; then \
		echo "Worker env file missing! Aborting workers creation."; exit 1; \
	fi

	gcloud compute instances create-with-container $(shell seq -f "parcs-worker-%g" 1 $(worker_count)) \
		--tags=parcs-instance \
		--container-image=registry.hub.docker.com/hummer12007/parcs-node \
		--container-env-file=$(worker_env_file) \
		--provisioning-model=SPOT \
		--zone=$(zone) \
		--project=$(project_id) \
		--machine-type=$(machine_type); 

delete-leader:
	gcloud compute instances delete parcs-leader --zone=$(zone) --project=$(project_id) --quiet

delete-workers:
	gcloud compute instances delete $(shell seq -f "parcs-worker-%g" 1 $(worker_count)) --zone=$(zone) --project=$(project_id) --quiet; \

delete-all: delete-workers delete-leader delete-firewall

start: workers leader