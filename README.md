# BananaEndocarp
BananaEndocarp is a scripted GUI for interacting with MunkiWebAdmin2's API.

Designed to be light-weight, portable, easy to modify, and maintain. BananaEndocarp sticks with a minimalist approach to creating manifests and follows the same principles as blogged about here: https://groob.io/posts/manifest-guide/.

Manifest within munki don't need to be complicated. This tool helps **automate the process of creating a unique manifest for each device** because that process can be tedious. This tool makes no assumptions about what your `included_manifests` look like. That task is up to you to design and create.

---

![example_gif](/resources/BananaEndocarpDemo.gif)

The above demo will result in a manifest that looks like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>catalogs</key>
	<array>
		<string>production</string>
	</array>
	<key>display_name</key>
	<string>011-115-maccb</string>
	<key>included_manifests</key>
	<array>
		<string>manifest C</string>
	</array>
	<key>managed_installs</key>
	<array>
	</array>
	<key>managed_uninstalls</key>
	<array>
	</array>
	<key>managed_updates</key>
	<array>
	</array>
	<key>optional_installs</key>
	<array>
	</array>
	<key>user</key>
	<string>clayton burlison</string>
</dict>
</plist>
```

## Documentation 
* Create an API user for use with mwa2. 
* Modify `BananaEndocarp.py` [variables](https://github.com/clburlison/BananaEndocarp/blob/nibbler/BananaEndocarp.py#L36-L62). 
* Run `make dmg`. 
* Throw the the `launchBananaEndocarp.sh` script into your Imagr workflow along with changing the path to the dmg. 
* Modify your imagr workflow. 
* Benefit.


I owe you some better documentation...



# Credits
Major thanks to:  

| Author  |  Project Link |
|---|---|
| [@pudquick](https://github.com/pudquick) | [nibbler](https://github.com/pudquick/nibbler) |
| [Munki](https://github.com/munki) | [MunkiWebAdmin2](https://github.com/munki/mwa2/) |