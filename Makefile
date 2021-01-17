.PHONY = all

all:
	cd maszyna_wirtualna && $(MAKE)
	mv ./maszyna_wirtualna/maszyna-wirtualna-cln ./vm
