VENV_ROOT=.venv
VENV=$(VENV_ROOT)/bin

APP=main:app

.PHONY: remove-venv
remove-venv:
	@echo "Removing venv"
	rm -rf $(VENV_ROOT)

.PHONY: venv
venv:
	@echo "Creating venv"
	python -m venv .venv

.PHONY: install
install: venv
	@echo "Installing Python packages"
	$(VENV)/python -m pip --disable-pip-version-check install -r requirements.txt

.PHONY: clean-install
clean-install: remove-venv install

.PHONY: run
run:
	@echo "Running app"
	$(VENV)/uvicorn $(APP) --port 5000

.PHONY: dev
dev: install
	@echo "Running app in dev mode"
	$(VENV)/uvicorn $(APP) --reload --port 5000