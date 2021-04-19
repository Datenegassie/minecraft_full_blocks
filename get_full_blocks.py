import os
import zipfile
import json

def get_data(version):
	try:
		jar = zipfile.ZipFile("{0}\\.minecraft\\versions\\{1}\\{1}.jar".format(os.getenv('APPDATA'),version)) # Get the requested Minecraft jar from %appdata%/.minecraft/versions
		# I might add support for custom filepaths in a future version.
	except:
		print("Version not found! Are you sure it's installed?")
		input("Press ENTER to continue.")
	for filename in jar.namelist():
		if filename.startswith("assets/minecraft/blockstates/") or filename.startswith("assets/minecraft/models/block/"):
			jar.extract(filename,"data\\{}\\".format(version))
	jar.close()

def get_fullblocks(version):
	fullblocks = []
	for filename in os.listdir("data/{}/assets/minecraft/blockstates".format(version)): # Check every file in the blockstates folder. This _should_ contain every block in the game.
		block = json.load(open("data/{}/assets/minecraft/blockstates/{}".format(version,filename)))
		try:
			variant = list(block["variants"].values())[0]
		except: # Triggered when there are no variants, like in multipart models such as fences. These are immediately discarded.
			continue
		if type(variant) is list:
			modelfile = variant[0]["model"][10:]
		else:
			modelfile = variant["model"][10:]
		for attempts in range(10): # Try multiple times for nested parents, but finitely to prevent infinite loops.
			try:
				model = json.load(open("data/{}/assets/minecraft/models/{}.json".format(version,modelfile)))
				parent = model["parent"]
				if parent.startswith("minecraft:"): # I have to do this check because Minecraft is inconsistent with using its own namespace as prefix.
					parent = parent[10:]
				if parent == "block/cube":
					fullblocks += [filename[:-5]]
					break
				else:
					modelfile = parent
			except: # Triggered when there is no defined parent. These are also discarded.
				break
	tag = {"replace":False,"values":fullblocks}
	tagfile = open("full_blocks_{}.json".format(version),"w")
	json.dump(tag,tagfile)

version = input("Enter the Minecraft version (Needs to be installed): ")
get_data(version)
get_fullblocks(version)
