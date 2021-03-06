import sublime, sublime_plugin, tempfile, base64, os, sys, mimetypes, json, ntpath, threading

sys.path.append( os.path.join( os.path.dirname( __file__ ), "requests" ) )
import requests
from requests.auth import HTTPBasicAuth

class CloudupCommand( sublime_plugin.TextCommand ):
	def run( self, edit ):
		# Grabs the current line or current selection
		selection = ''
		for region in self.view.sel():
			line = self.view.line(region)
			selection += self.view.substr(line) + '\n'

		# Create a temporary file with the contents that we can upload
		tmpfile = tempfile.NamedTemporaryFile( delete = False )
		tmpfile.write( bytes( selection.encode( 'utf8' ) ) )
		tmpfile.close()

		# Get it.. upload? Cloudupload?
		sublime.status_message( 'Starting Cloudup upload...' )
		thread = Cloudupload( tmpfile.name, 'selection' )
		thread.start()

class CloudupFileCommand( sublime_plugin.TextCommand ):
	def run ( self, edit ):
		# the currently opened file
		currentfile = self.view.file_name()
		sublime.status_message( 'Starting Cloudup upload...' )
		thread = Cloudupload( currentfile, 'file' )
		thread.start()

class CloudupSidebar( sublime_plugin.WindowCommand ):
	def run(self, paths = [] ):
		sublime.status_message( 'Starting Cloudup upload...' )
		threads = []
		for item in paths:
			if os.path.isdir( item ):
				title = str( ntpath.basename( item ) )
				auth = HTTPBasicAuth( Cloudupload.auth_username(), Cloudupload.auth_password() )
				s = requests.post( 'https://api.cloudup.com/1/streams', data = { 'title': title }, auth = auth )
				if s.status_code != 201:
					sublime.error_message( 'Cloudup connection failed. Please check your username/password and try again' )
					return
				stream = s.json()

				for root, subFolders, files in os.walk( item ):
					for file in files:
						if file != '.DS_Store':
							thread = Cloudupload( os.path.join( root, file ), 'file', str( stream['id'] ) )
							threads.append( thread )
							thread.start()

				url = 'https://cloudup.com/' + stream['id']
				sublime.set_clipboard( url )
				sublime.status_message( 'File(s) uploaded. ' + url + ' copied to clipboard' )
			else:
				thread = Cloudupload( item, 'file' )
				thread.start()

class Cloudupload(threading.Thread):

	def __init__(self, thefile, type, stream_id = '' ):  
		self.thefile = thefile
		self.type = type
		self.stream_id = stream_id
		threading.Thread.__init__(self) 

	def run(self):
		auth = HTTPBasicAuth( Cloudupload.auth_username(), Cloudupload.auth_password() )

		if self.type == 'file':
			title = str( ntpath.basename( self.thefile ) )
		else:
			title = 'Untitled Snippet'

		# Create a new stream for this snippet if we didn't already pass it one..
		if self.stream_id == '':
			s = requests.post( 'https://api.cloudup.com/1/streams', data = { 'title': title }, auth = auth )
			if s.status_code != 201:
				sublime.error_message( 'Cloudup connection failed. Please check your username/password and try again' )
				return
			stream = s.json()
			self.stream_id = stream['id']
			multi = False
		else:
			multi = True

		# Create a new item inside the stream with some starter information
		file_data = { 'filename': self.thefile, 'stream_id': self.stream_id }
		i = requests.post( 'https://api.cloudup.com/1/items', data = file_data, auth = auth )
		if i.status_code != 201:
			sublime.error_message( 'Cloudup connection failed. Please check your username/password and try again' )
			return
		item = i.json()

		# Now we need to physically upload the file to Amazon using the s3 details we got from item
		s3_data = {
			'key': item['s3_key'],
			'Content-Type': 'text/plain',
			'Content-Length': os.path.getsize( self.thefile ),
			'AWSAccessKeyId': item['s3_access_key'],
			'acl': 'public-read',
			'policy': item['s3_policy'],
			'signature': item['s3_signature']
		}

		files = {
			'file': open( self.thefile, 'rb' )
		}

		s3 = requests.post( item['s3_url'], files = files, data = s3_data )
		if s3.status_code != 204:
			sublime.error_message( 'Cloudup connection failed. Please check your username/password and try again' )
			return
	
		# Finally, we need to let Cloudup know that the upload was successful
		body = json.dumps( { u"complete": True } )
		headers = { 'Content-Type': 'application/json' }
		complete = requests.patch( url = 'https://api.cloudup.com/1/items/' + item['id'], data = body, headers = headers, auth = auth )
		if complete.status_code != 200:
			sublime.error_message( 'Cloudup connection failed. Please check your username/password and try again' )
			return

		if multi == False:
			sublime.set_clipboard( item['url'] )
			if self.type == 'file':
				sublime.status_message( 'File uploaded. ' + item['url'] + ' copied to clipboard' )
			else:
				sublime.status_message( 'Selection uploaded. ' + item['url'] + ' copied to clipboard' )

	def auth_username():
		settings = sublime.load_settings( 'Cloudup.sublime-settings' )
		username = settings.get( 'username' )
		if not username:
			sublime.error_message( "Please provide your username in the Cloudup.sublime-settings file." )
		return username

	def auth_password():
		settings = sublime.load_settings( 'Cloudup.sublime-settings' )
		password = settings.get( 'password' )
		if not password:
			sublime.error_message( "Please provide your password in the Cloudup.sublime-settings file." )
		return password