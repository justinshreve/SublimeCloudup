import sublime, sublime_plugin, tempfile, base64, os, sys, mimetypes, json

sys.path.append( os.path.join( os.path.dirname( __file__ ), "requests" ) )
import requests
from requests.auth import HTTPBasicAuth

global settings

class CloudupCommand( sublime_plugin.TextCommand ):
	def run( self, edit ):
		global settings
		settings = sublime.load_settings( 'Cloudup.sublime-settings' )
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
		Cloudupload( tmpfile )

class Cloudupload:
	def __init__( self, thefile ):
		auth = HTTPBasicAuth( self.auth_username(), self.auth_password() )

		# Create a new stream for this snippet
		s = requests.post( 'https://api.cloudup.com/1/streams', data = { 'title': 'Untitled Snippet' }, auth = auth )
		if s.status_code != 201:
			sublime.error_message( 'Snippet creation failed. Please check your username/password and try again' )
			return
		stream = s.json()

		# Create a new item inside the stream with some starter information
		file_data = { 'filename': thefile.name, 'mime': 'text/plain', 'stream_id': stream['id'] }
		i = requests.post( 'https://api.cloudup.com/1/items', data = file_data, auth = auth )
		if i.status_code != 201:
			sublime.error_message( 'Snippet creation failed. Please check your username/password and try again' )
			return
		item = i.json()

		# I'm just learning python - is there a better way to get the file size here?
		f = open( thefile.name, 'rb' )
		size = len( f.read() )
		f.close()

		# Now we need to physically upload the file to Amazon using the s3 details we got from item
		s3_data = {
			'key': item['s3_key'],
			'Content-Type': 'text/plain', # @todo: be smarter about this?
			'Content-Length': size,
			'AWSAccessKeyId': item['s3_access_key'],
			'acl': 'public-read',
			'policy': item['s3_policy'],
			'signature': item['s3_signature']
		}

		files = {
			'file': open( thefile.name, 'rb' )
		}

		s3 = requests.post( item['s3_url'], files = files, data = s3_data )
		if s3.status_code != 204:
			sublime.error_message( 'Snippet creation failed. Please check your username/password and try again' )
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
		username = settings.get( 'username' )
		if not username:
			sublime.error_message( "Please provide your username in the Cloudup.sublime-settings file." )
		return username

	def auth_password( self ):
		password = settings.get( 'password' )
		if not password:
			sublime.error_message( "Please provide your password in the Cloudup.sublime-settings file." )
		return password