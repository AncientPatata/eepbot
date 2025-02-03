.PHONY: init
init: 
	mkdir -p ./deployment/seq

.PHONY: build
rebuild-bot: 
	cd eepbot_deploy
	terraform taint docker_image.eepbot
	terraform apply -auto-approve 

.PHONY: 
deploy: 
	cd eepbot_deploy
	terraform apply -auto-approve 

.PHONY: destroy
destroy: 
	cd eepbot_deploy
	terraform destroy -auto-approve