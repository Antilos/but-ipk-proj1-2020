HOST = 127.0.0.1
PORT = 5353

PYTHON = python3
SRC = src
ARCHIVE = xkocal00.zip

.PHONY = zip build clean

all: build

build: $(SRC)/server.py
	$(PYTHON) $^ $(HOST) $(PORT)

zip: $(SRC) $(SRC)/server.py $(SRC)/ipk_exceptions.py readme.md
	zip $(ARCHIVE) $^ Makefile

clean:
	rm $(ARCHIVE)