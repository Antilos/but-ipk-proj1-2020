HOST = 127.0.0.1
PORT = 5353

PYTHON = python3
SRC = src

all: build

build: $(SRC)/server.py
	$(PYTHON) $^ $(HOST) $(PORT)