# BananaEndocarp
In its current form BananaEndocarp is a script for interacting with MunkiWebAdmin2's API. it uses [@pudquick](https://github.com/pudquick)'s [nibbler](https://gist.github.com/pudquick/f27efd1ddcbf57be0d14031a5e692015). BananaEndocarp serves the same purpose as [Munki Enroll](https://github.com/edingc/munki-enroll) however it creates manifests in a flat format, all files go under `/manifests` in your munki repo based off of the serial number. It also has two optional fields "User Name" and "Hostname". These two fields help when making changes to manifests and sorting later.

This has been tested and works great with Imagr.

![example_gif](/resources/BananaEndocarpDemo.gif)

## Documentation 
* Create an API user for use with mwa2. 
* Modify `BananaEndocarp.py` [variables](https://github.com/clburlison/BananaEndocarp/blob/nibbler/BananaEndocarp.py#L36-L55). 
* Run `make dmg`. 
* Throw the the `launchBananaEndocarp.sh` script into your Imagr work along with changing the path to the dmg. 
* Modify your imagr workflow. Benefit.


I owe you some better documentation...