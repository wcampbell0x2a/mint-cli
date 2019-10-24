VERSION=v0.2.0

all: docs
	sed -i "s/VERSION/$(VERSION)/g" mint-cli.scdoc
	scdoc < mint-cli.scdoc > mint-cli.1

install:
	install -m 644 ./mint-cli.1 /usr/local/man/man1/

uninstall:
	rm -f /usr/local/man/man1/mint-cli.1
