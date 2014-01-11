ZIP_FILE = blobber-$(shell date -u "+%Y-%m-%d-%H-%M").zip

eb:
	-rm -f $(ZIP_FILE)
	zip -r $(ZIP_FILE) \
	    application.py blobber .ebextensions requirements.txt
