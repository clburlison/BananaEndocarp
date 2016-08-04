# Makefile for BananaEndocarp related tasks

PROJECT="BananaEndocarp"

#################################################

##Help - Show this help menu
help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##  dmg - Wrap the scripts inside a dmg
dmg:
	rm -f ./${PROJECT}.dmg
	rm -rf /tmp/${PROJECT}-build
	mkdir -p /tmp/${PROJECT}-build/
	cp -R {README.md,BananaEndocarp.nib,BananaEndocarp.py,nibbler.py} /tmp/${PROJECT}-build
	hdiutil create -srcfolder /tmp/${PROJECT}-build -volname "${PROJECT}" -format UDRW -o ${PROJECT}.dmg
	rm -rf /tmp/${PROJECT}-build
