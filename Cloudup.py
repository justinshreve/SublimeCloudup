import sublime, sublime_plugin, tempfile, base64, os, sys, mimetypes, json, ntpath

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
		Cloudupload( tmpfile.name, 'selection' )

class CloudupFileCommand( sublime_plugin.TextCommand ):
	def run ( self, edit ):
		# the currently opened file
		currentfile = self.view.file_name()
		Cloudupload( currentfile, 'file' )

class Cloudupload:
	def __init__( self, thefile, type ):
		auth = HTTPBasicAuth( self.auth_username(), self.auth_password() )

		if type == 'file':
			title = str( ntpath.basename( thefile ) )
		else:
			title = 'Untitled Snippet'

		# Create a new stream for this snippet
		s = requests.post( 'https://api.cloudup.com/1/streams', data = { 'title': title }, auth = auth )
		if s.status_code != 201:
			sublime.error_message( 'Cloudup connection failed. Please check your username/password and try again' )
			return
		stream = s.json()

		# Create a new item inside the stream with some starter information
		file_data = { 'filename': thefile, 'mime': 'text/plain', 'stream_id': stream['id'] }
		i = requests.post( 'https://api.cloudup.com/1/items', data = file_data, auth = auth )
		if i.status_code != 201:
			sublime.error_message( 'Cloudup connection failed. Please check your username/password and try again' )
			return
		item = i.json()

		# Now we need to physically upload the file to Amazon using the s3 details we got from item
		s3_data = {
			'key': item['s3_key'],
			'Content-Type': 'text/plain', # @todo: be smarter about this?
			'Content-Length': os.path.getsize( thefile ),
			'AWSAccessKeyId': item['s3_access_key'],
			'acl': 'public-read',
			'policy': item['s3_policy'],
			'signature': item['s3_signature']
		}

		files = {
			'file': open( thefile, 'rb' )
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
			sublime.error_message( 'Snippet creation failed. Please check your username/password and try again' )
			return
		
		sublime.set_clipboard( item['url'] )
		sublime.status_message( item['url'] + ' copied to clipboard' )

	def auth_username( self ):
		settings = sublime.load_settings( 'Cloudup.sublime-settings' )
		username = settings.get( 'username' )
		if not username:
			sublime.error_message( "Please provide your username in the Cloudup.sublime-settings file." )
		return username

	def auth_password( self ):
		settings = sublime.load_settings( 'Cloudup.sublime-settings' )
		password = settings.get( 'password' )
		if not password:
			sublime.error_message( "Please provide your password in the Cloudup.sublime-settings file." )
		return password