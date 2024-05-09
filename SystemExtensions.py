import os

def GetAllFilePathsOfType (rootFolderPath : str, fileExtension : str) -> list[str]:
	output = []
	foldersRemaining = [ rootFolderPath ]
	while len(foldersRemaining) > 0:
		folderPath = foldersRemaining[0]
		for path in os.listdir(folderPath):
			fullPath = folderPath + '/' + path
			if os.path.isdir(fullPath):
				foldersRemaining.append(fullPath)
			elif os.path.isfile(fullPath) and fullPath.endswith(fileExtension):
				output.append(fullPath)
		del foldersRemaining[0]
	return output