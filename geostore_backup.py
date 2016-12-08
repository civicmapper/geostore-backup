""" See the
associated README.md for more information.
"""

# --------------------------------------------------------------
# IMPORTS

# standard library imports
import sys, os, logging, zipfile, json, time, errno, shutil, traceback, inspect

# Import ArcREST (v2)
import arcrest
#from arcresthelper import securityhandlerhelper, common
from arcresthelper import common
from arcrest.security import AGOLTokenSecurityHandler
from arcrest.agol import FeatureService
from arcrest.common.filters import LayerDefinitionFilter

## Import zlib for zip file compression if available
try:
	import zlib
	compression = zipfile.ZIP_DEFLATED
except:
	compression = zipfile.ZIP_STORED

# --------------------------------------------------------------
# PARAMETERS

out_path = sys.argv[1]
""" local\\path\\to\\save\\backups
"""

username = sys.argv[2]
"""AGOL or AGS username
"""

password = sys.argv[3]
"""AGOL or AGS password
"""

backups_json = sys.argv[4]
""" local\\path\\to\\.json backups config file

	example of json:
	
	{
		"Name of thing to be backed up":
		{
			"url": "http://services1.arcgis.com/vdNDkVykv9vEWFX4/ArcGIS/rest/services/3RWW_Atlas_Green_Infrastructure_Inventory/FeatureServer",
			"layers": [0]
		}
	}
"""

def trace():
	"""error catching
	"""
	tb = sys.exc_info()[2]
	tbinfo = traceback.format_tb(tb)[0]
	filename = inspect.getfile(inspect.currentframe())
	# script name + line number
	line = tbinfo.split(", ")[1]
	# Get Python syntax error
	synerror = traceback.format_exc().splitlines()[-1]
	return line, filename, synerror

def timestamp():
	"""return current date/time as a string: "yyyymmddHHMMSS"
	"""
	return time.strftime("%Y%m%d_%H%M%S", time.localtime())

if __name__ == "__main__":

	try:

		print("Running GeoStore Backup...")

		# load the json backup config file
		backups = json.load(open(backups_json,'r'))

		# make directory backups
		if not os.path.exists(out_path):
			os.makedirs(out_path)

		# make a llg file
		logfile = os.path.join(out_path, 'geostore_backup.log')
		logging.basicConfig(
			filename=logfile,
			level=logging.INFO,
			format='%(asctime)s %(message)s'
		)
		
		# create log in object
		print("Creating security handler...")
		agolSH = AGOLTokenSecurityHandler(
			username=username,
			password=password)

		# iterate through backup dictionary
		for k, v in backups.items():
			msg = "Backing up {0}".format(k)
			print(msg)
			#logging.info(msg)

			#check for and/or make a folder with the service name
			backup_path = os.path.join(out_path,k)
			if not os.path.exists(backup_path):
				os.makedirs(backup_path)

			#check for and/or make a folder with the date
			archive_path = os.path.join(backup_path,timestamp())
			if not os.path.exists(archive_path):
				os.makedirs(archive_path)

			proxy_port = None
			proxy_url = None
			url = backups[k]["url"]

			msg2 = "Accessing service @ {0}".format(url)
			logging.info(msg2)
			print(msg2)
			fs = FeatureService(
				url=url,
				securityHandler=agolSH,
				proxy_port=proxy_port,
				proxy_url=proxy_url,
				initialize=True)

			print("Copying service to {0}".format(out_path))
			result = fs.createReplica(
				replicaName=backups[k],
				layers=backups[k]["layers"],
				keep_replica=False,
				layerQueries=None,
				geometryFilter=None,
				returnAttachments=True,
				returnAttachmentDatabyURL=False,
				returnAsFeatureClass=True,
				out_path=archive_path)
			
			#for each downloaded file geodatabase (which is just a folder)
			for each_folder in result:
				try:
					# make a zip file with the same name as the archive directory
					zipped_output = os.path.join(
						archive_path,
						"{0}.zip".format(os.path.basename(archive_path))
					)
					print("Zipping up backup to {0}".format(zipped_output))
					# create a zip file object
					zf = zipfile.ZipFile(zipped_output, mode="w")
					
					# get the name of the fgdb folder
					folder_name = os.path.basename(each_folder)
					
					# get all of its files
					files_in_dir = []
					for dir_entry in os.listdir(each_folder):
						dir_entry_path = os.path.join(each_folder, dir_entry)
						if os.path.isfile(dir_entry_path):
							files_in_dir.append(dir_entry_path)
					# write those files to the zip archive
					for each_file in files_in_dir:
						# note that arcname includes the original fgdb folder name,
						# so we're not just dumping fgdb contents into a zip
						zf.write(
							filename=each_file,
							arcname=os.path.join(
								folder_name, os.path.basename(each_file)
							),
							compress_type=compression
						)
					# delete the original downloaded fgdb
					shutil.rmtree(each_folder)
				finally:
					zf.close()
					msg3 = "{0} service backed-up to: {1}".format(k, zipped_output)
					logging.info(msg3)
					print(msg3)



	except (common.ArcRestHelperError),e:
		errors = [
			"error in function: %s" % e[0]['function'],
			"error on line: %s" % e[0]['line'],
			"error in file name: %s" % e[0]['filename'],
			"with error message: %s" % e[0]['synerror'],
			]
		for es in errors:
			print(es)
			logging.ERROR(es)
		if 'arcpyError' in e[0]:
			print("with arcpy message: %s" % e[0]['arcpyError'])
			logging.ERROR(es)
	except:
		line, filename, synerror = trace()
		print("error on line: %s" % line)
		print("error in file name: %s" % filename)
		print("with error message: %s" % synerror)
