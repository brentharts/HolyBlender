import bpy, subprocess, os, sys, hashlib, mathutils, math, base64, webbrowser

user_args = None
for arg in sys.argv:
	if arg == '--': user_args = []
	elif type(user_args) is list: user_args.append(arg)
if user_args: print('user_args:', user_args)

__thisdir = os.path.split(os.path.abspath(__file__))[0]
sys.path.append( __thisdir )
sys.path.append( os.path.join(__thisdir, 'Blender_bevy_components_workflow/tools') )
print(sys.path)
import bevy_components
print(bevy_components)
import gltf_auto_export
print(gltf_auto_export)
bpy.ops.preferences.addon_enable(module='bevy_components')
bpy.ops.preferences.addon_enable(module='gltf_auto_export')

sys.path.append(os.path.join(__thisdir, 'Extensions'))
from SystemExtensions import *
from StringExtensions import *
from CollectionExtensions import *

if os.path.isdir(os.path.join(__thisdir,'Net-Ghost-SE')):
	sys.path.append(os.path.join(__thisdir,'Net-Ghost-SE'))
	import ghostblender
	print(ghostblender)
else:
	ghostblender = None

bl_info = {
	'name': 'HolyBlender',
	'blender': (2, 80, 0),
	'category': 'System',
}
REPLACE_INDICATOR = 'ꗈ'
EXAMPLES_DICT = {
	'Hello World (Unity)' : '''using UnityEngine;

public class HelloWorld : MonoBehaviour
{
	void Start ()
	{
		print("Hello World!");
	}
}''',
	'Rotate (Unity)': '''using UnityEngine;

public class Rotate : MonoBehaviour
{
	public float rotateSpeed = 50.0f;

	void Update ()
	{
		transform.eulerAngles += Vector3.up * rotateSpeed * Time.deltaTime;
	}
}''',
	'Grow And Shrink (Unity)': '''using UnityEngine;

public class GrowAndShrink : MonoBehaviour
{
	public float maxSize = 5.0f; 
	public float minSize = 0.2f;
	public float speed = 0.375f;

	void Update ()
	{
		transform.localScale = Vector3.one * (((Mathf.Sin(speed * Time.time) + 1) / 2) * (maxSize - minSize) + minSize);
	}
}''',
	'Keyboard And Mouse Controls (Unity)' : '''using UnityEngine;

public class WASDAndMouseControls : MonoBehaviour
{
	public float moveSpeed = 5.0f;

	void Update ()
	{
		Vector3 move = Vector3.zero;
		if (Input.GetKey(KeyCode.A))
			move.x -= 1.0f;
		if (Input.GetKey(KeyCode.D))
			move.x += 1.0f;
		if (Input.GetKey(KeyCode.S))
			move.y -= 1.0f;
		if (Input.GetKey(KeyCode.W))
			move.y += 1.0f;
		move.Normalize();
		transform.position += move * moveSpeed * Time.deltaTime;
		Vector3 mousePosition = Camera.main.ScreenToWorldPoint(Mouse.current.position.ReadValue());
		transform.up = mousePosition - transform.position;
	}
}''',
	'First Person Controls (Unity) (Unfinished)' : '''using UnityEngine;
using UnityEngine.InputSystem;

public class FirstPersonControls : MonoBehaviour
{
	public float moveSpeed = 5.0f;
	public float lookSpeed = 50.0f;
	Vector2 previousMousePosition;

	void Update ()
	{
		Vector3 move = Vector3.zero;
		if (Keyboard.current.aKey.isPressed)
			move.x -= 1.0f;
		if (Keyboard.current.dKey.isPressed)
			move.x += 1.0f;
		if (Keyboard.current.sKey.isPressed)
			move.y -= 1.0f;
		if (Keyboard.current.wKey.isPressed)
			move.y += 1.0f;
		move.Normalize();
		transform.position += move * moveSpeed * Time.deltaTime;
		Vector2 mousePosition = Mouse.current.position.ReadValue();
		Vector2 look = (mousePosition - previousMousePosition) * lookSpeed;
		transform.Rotate(new Vector3(look.y, look.x));
		previousMousePosition = mousePosition;
	}
}''',
	'Hello World (bevy)' : 'println!("Hello World!");',
	'Rotate (bevy)' : 'trs.rotate_y(5.0 * time.delta_seconds());)'
}
INIT_HTML = '''
<script>
function Test ()
{
	alert("Ok");
	//TODO xmlhttprequest
}
</script>
<button onclick="Test ()">Hello World!</button>
<a href="/bpy/data/objects/Cube">Cube</a>
'''
BLENDER_SERVER = '''
import bpy, json, base64, mathutils
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

LOCALHOST_PORT = 8000
POLL_INDICATOR = 'poll?'
JOIN_INDICATOR = 'join?'
LEFT_INDICATOR = 'left?'
JSON_INDICATOR = 'exec?'

events = []
clientIds = []
lastClientId = 0
unsentClientsEventsDict = {}

class BlenderServer (BaseHTTPRequestHandler):
	def do_GET (self):
		global events
		global clientIds
		global lastClientId
		global unsentClientsEventsDict
		self.send_response(200)
		self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
		self.send_header('Pragma', 'no-cache')
		self.send_header('Expires', '0')
		ret = 'OK'
		clientId = -1
		data = ''
		urlComponents = self.path.split('?')
		if len(urlComponents) > 1:
			clientId = urlComponents[-2]
			try:
				clientId = int(clientId)
			except:
				print('Player ' + str(lastClientId) + ' joined')
			data = urlComponents[-1]
		if self.path.endswith('.ico'):
			pass
		elif self.path == '/':
			if '__index__.html' in bpy.data.texts:
				ret = bpy.data.texts['__index__.html'].as_string()
			else:
				for t in bpy.data.texts:
					if t.name.endswith('.html'):
						ret = t.as_string()
						break
		elif self.path.startswith('/bpy/data/objects/'):
			name = self.path.split('/')[-1]
			if name in bpy.data.objects:
				ret = str(bpy.data.objects[name])
		elif os.path.isfile(self.path[1:]): # The .wasm file
			ret = open(self.path[1:], 'rb').read()
		elif self.path.endswith('.glb'):
			bpy.ops.object.select_all(action='DESELECT')
			name = self.path.split('/')[-1][: -len('.glb')]
			if name in bpy.data.objects:
				ob = bpy.data.objects[name]
				ob.select_set(True)
				tmp = '/tmp/__httpd__.glb'
				bpy.ops.export_scene.gltf(filepath=tmp, export_selected = True)
				ret = open(tmp,'rb').read()
		elif data in bpy.data.objects:
			ret = str(bpy.data.objects[data])
		elif self.path[1 :].startswith(JOIN_INDICATOR):
			clientIds.append(lastClientId)
			unsentClientsEventsDict[lastClientId] = events
			ret = str(lastClientId)
			lastClientId += 1
		elif self.path[1 :].startswith(LEFT_INDICATOR):
			clientIds.remove(clientId)
			del unsentClientsEventsDict[clientId]
		elif self.path[1 :].startswith(JSON_INDICATOR):
			jsonText = data
			jsonText = jsonText.encode("ascii")
			jsonText = base64.b64decode(jsonText)
			jsonText = jsonText.decode("ascii")
			jsonData = json.loads(jsonText)
			events.append(jsonData)
			obj = bpy.data.objects[jsonData['objectName']]
			valueName = jsonData['valueName']
			value = jsonData['value']
			if valueName == 'location':
				obj.location = mathutils.Vector((float(value['x']), float(value['y']), float(value['z'])))
			for _clientId in clientIds:
				if _clientId != clientId:
					unsentClientsEventsDict[_clientId].append(jsonData)
		else: # elif self.path[1 :].startswith(POLL_INDICATOR):
			ret = ''
			for event in unsentClientsEventsDict[clientId]:
				ret += str(event) + \'\\n\'
			unsentClientsEventsDict[clientId].clear()
		if ret is None:
			ret = 'None?'
		if type(ret) is not bytes:
			ret = ret.encode('utf-8')
		self.send_header('Content-Length', str(len(ret)))
		self.end_headers()
		try:
			self.wfile.write(ret)
		except BrokenPipeError:
			print('CLIENT WRITE ERROR: failed bytes', len(ret))

httpd = HTTPServer(('localhost', LOCALHOST_PORT), BlenderServer)
httpd.timeout=0.1
print(httpd)
timer = None
@bpy.utils.register_class
class HttpServerOperator (bpy.types.Operator):
	'HolyBlender HTTP Server'
	bl_idname = 'httpd.run'
	bl_label = 'httpd'
	bl_options = {'REGISTER'}

	def modal (self, context, event):
		if event.type == 'TIMER' and HTTPD_ACTIVE:
			httpd.handle_request() # Blocks for a short time
		return {'PASS_THROUGH'} # Doesn't supress event bubbles

	def invoke (self, context, event):
		global timer
		if timer is None:
			timer = self._timer = context.window_manager.event_timer_add(
				time_step=0.033333334,
				window=context.window
			)
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		return {'FINISHED'}

	def execute (self, context):
		return self.invoke(context, None)

HTTPD_ACTIVE = True
bpy.ops.httpd.run()'''
WATTS_TO_CANDELAS = 0.001341022
PI = 3.141592653589793
UNITY_SCRIPTS_PATH = os.path.join(__thisdir, 'Unity Scripts')
GODOT_SCRIPTS_PATH = os.path.join(__thisdir, 'Godot Scripts')
EXTENSIONS_PATH = os.path.join(__thisdir, 'Extensions')
TEMPLATES_PATH = os.path.join(__thisdir, 'Templates')
TEMPLATE_REGISTRY_PATH = os.path.join(TEMPLATES_PATH, 'registry.json')
REGISTRY_PATH = os.path.join('/tmp', 'registry.json')
MAX_SCRIPTS_PER_OBJECT = 16
unrealCodePath = ''
unrealCodePathSuffix = os.path.join('', 'Source', '')
excludeItems = [ os.path.join('', 'Library') ]
operatorContext = None
currentTextBlock = None
mainClassNames = []
attachedUnityScriptsDict = {}
attachedUnrealScriptsDict = {}
attachedGodotScriptsDict = {}
attachedBevyScriptsDict = {}
previousRunningScripts = []
textBlocksTextsDict = {}
previousTextBlocksTextsDict = {}
propertiesDefaultValuesDict = {}
propertiesTypesDict = {}
childrenDict = {}

class WorldPanel (bpy.types.Panel):
	bl_idname = 'WORLD_PT_World_Panel'
	bl_label = 'HolyBlender Export'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'world'

	def draw(self, context):
		self.layout.prop(context.world, 'unity_project_import_path')
		self.layout.prop(context.world, 'unity_project_export_path')
		self.layout.prop(context.world, 'unrealExportPath')
		self.layout.prop(context.world, 'godotExportPath')
		self.layout.prop(context.world, 'bevy_project_path')
		self.layout.prop(context.world, 'htmlExportPath')
		self.layout.prop(context.world, 'holyserver')
		self.layout.prop(context.world, 'html_code')
		self.layout.operator(UnityExportButton.bl_idname, icon='CONSOLE')
		self.layout.operator(UnrealExportButton.bl_idname, icon='CONSOLE')
		self.layout.operator(GodotExportButton.bl_idname, icon='CONSOLE')
		self.layout.operator(BevyExportButton.bl_idname, icon='CONSOLE')
		self.layout.operator(HTMLExportButton.bl_idname, icon='CONSOLE')
		self.layout.operator(PlayButton.bl_idname, icon='CONSOLE')

class UnityScriptsPanel (bpy.types.Panel):
	bl_idname = 'OBJECT_PT_Unity_Scripts_Panel'
	bl_label = 'HolyBlender Unity Scripts'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'object'

	def draw(self, context):
		self.layout.label(text='Attach Unity scripts')
		foundUnassignedScript = False
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			hasProperty = getattr(context.active_object, 'unity_script' + str(i)) != None
			if hasProperty or not foundUnassignedScript:
				self.layout.prop(context.active_object, 'unity_script' + str(i))
			if not foundUnassignedScript:
				foundUnassignedScript = not hasProperty

class UnrealScriptsPanel (bpy.types.Panel):
	bl_idname = 'OBJECT_PT_Unreal_Scripts_Panel'
	bl_label = 'HolyBlender Unreal Scripts'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'object'

	def draw(self, context):
		self.layout.label(text='Attach Unreal scripts')
		foundUnassignedScript = False
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			hasProperty = getattr(context.active_object, 'unreal_script' + str(i)) != None
			if hasProperty or not foundUnassignedScript:
				self.layout.prop(context.active_object, 'unreal_script' + str(i))
			if not foundUnassignedScript:
				foundUnassignedScript = not hasProperty

class GodotScriptsPanel (bpy.types.Panel):
	bl_idname = 'OBJECT_PT_Godot_Scripts_Panel'
	bl_label = 'HolyBlender Godot Scripts'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'object'

	def draw(self, context):
		self.layout.label(text='Attach Godot scripts')
		foundUnassignedScript = False
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			hasProperty = getattr(context.active_object, 'godotScript' + str(i)) != None
			if hasProperty or not foundUnassignedScript:
				self.layout.prop(context.active_object, 'godotScript' + str(i))
			if not foundUnassignedScript:
				foundUnassignedScript = not hasProperty

class BevyScriptsPanel (bpy.types.Panel):
	bl_idname = 'OBJECT_PT_bevy_Scripts_Panel'
	bl_label = 'HolyBlender Bevy Scripts'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'object'

	def draw(self, context):
		self.layout.label(text='Attach bevy scripts')
		foundUnassignedScript = False
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			hasProperty = getattr(context.active_object, 'bevy_script' + str(i)) != None
			if hasProperty or not foundUnassignedScript:
				self.layout.prop(context.active_object, 'bevy_script' + str(i))
			if not foundUnassignedScript:
				foundUnassignedScript = not hasProperty

class ExamplesOperator (bpy.types.Operator):
	bl_idname = 'u2m.show_template'
	bl_label = 'Add or Remove'
	template : bpy.props.StringProperty(default = '')

	def invoke (self, context, event):
		if context.edit_text != None:
			context.edit_text.from_string(EXAMPLES_DICT[self.template])
		return {'FINISHED'}

class ExamplesMenu (bpy.types.Menu):
	bl_idname = 'TEXT_MT_u2m_menu'
	bl_label = 'HolyBlender Templates'

	def draw (self, context):
		layout = self.layout
		for name in EXAMPLES_DICT:
			op = layout.operator('u2m.show_template', text=name)
			op.template = name

class AttachedObjectsMenu (bpy.types.Menu):
	bl_idname = 'TEXT_MT_u2m_menu_obj'
	bl_label = 'HolyBlender Attached Objects'

	def draw (self, context):
		layout = self.layout
		if not context.edit_text:
			layout.label(text='No text block')
			return
		objs = []
		for obj in bpy.data.objects:
			attachedScripts = attachedUnityScriptsDict.get(obj, [])
			if context.edit_text.name in attachedScripts:
				objs.append(obj)
			attachedScripts = attachedBevyScriptsDict.get(obj, [])
			if context.edit_text.name in attachedScripts:
				objs.append(obj)
			attachedScripts = attachedUnrealScriptsDict.get(obj, [])
			if context.edit_text.name in attachedScripts:
				objs.append(obj)
		if objs:
			for obj in objs:
				layout.label(text=obj.name)
		else:
			layout.label(text='Script not attached to any objects')

class PlayButton (bpy.types.Operator):
	bl_idname = 'blender.play'
	bl_label = 'Start Playing (Unfinished)'

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		for textBlock in bpy.data.texts:
			textBlock.run_cs = True

class HTMLExportButton (bpy.types.Operator):
	bl_idname = 'html.export'
	bl_label = 'Export To HTML'

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		htmlExportPath = os.path.expanduser(context.scene.world.htmlExportPath)
		previousVisibleObjects = []
		for obj in bpy.data.objects:
			if obj.type == 'MESH' and not obj.hide_get():
				previousVisibleObjects.append(obj)
				obj.hide_render = True
		bpy.context.scene.render.resolution_percentage = 10
		camera = bpy.data.cameras[0]
		cameraObj = bpy.data.objects[camera.name]
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.view_layer.objects.active = cameraObj
		cameraObj.select_set(True)
		bpy.context.scene.camera = cameraObj
		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				area.spaces.active.region_3d.view_perspective = 'CAMERA'
				break
		bpy.context.scene.render.film_transparent = True
		bpy.context.scene.render.image_settings.color_mode = 'RGBA'
		previousCameraLocation = cameraObj.location
		previousCameraRotationMode = cameraObj.rotation_mode
		cameraObj.rotation_mode = 'XYZ'
		previousCameraRotation = cameraObj.rotation_euler
		previousCameraType = camera.type
		camera.type = 'ORTHO'
		previousCameraOrthoScale = camera.ortho_scale
		html = [
			'<!DOCTYPE html>',
			'<html><head><script>',
		]
		js_blocks = {}
		imgs = []
		for obj in bpy.data.objects:
			if obj.type == 'MESH':
				obj.hide_render = False
				bpy.context.scene.render.filepath = htmlExportPath + '/' + obj.name
				cameraObj.rotation_euler = mathutils.Vector((math.radians(90), 0, 0))
				bounds = GetObjectBounds(obj)
				cameraObj.location = bounds[0] - mathutils.Vector((0, bounds[1].y, 0))
				camera.ortho_scale = max(bounds[1].x, bounds[1].z) * 2
				if os.path.isfile( htmlExportPath + '/' + obj.name ) and '--skip-render' in sys.argv:
					pass
				else:
					bpy.ops.render.render(animation=False, write_still=True)
				obj.hide_render = True
				imagePath = bpy.context.scene.render.filepath + '.png'
				command = [ 'convert', '-delay', '10', '-loop', '0', imagePath, imagePath.replace('.png', '.gif') ]
				subprocess.check_call(command)
				imagePath = imagePath.replace('.png', '.gif')
				cameraSize = mathutils.Vector((camera.sensor_width, camera.sensor_height))
				imageData = open(imagePath, 'rb').read()
				base64EncodedStr = base64.b64encode(imageData).decode('utf-8')
				multiplyUnits = 50
				zIndex = int(bounds[0].y)
				zIndex += 10
				if zIndex < 0:
					zIndex = 0
				onclick =  ''
				if obj.html_on_click:
					fname = '__on_click_' + obj.html_on_click.name.replace('.','_')
					if obj.html_on_click.name not in js_blocks:
						js = 'function %s(self){%s}' % (fname, obj.html_on_click.as_string())
						js_blocks[obj.html_on_click.name] = js
					onclick = 'javascript:%s(this)' % fname
				userCss = ''
				if obj.html_css:
					userCss = obj.html_css.as_string().replace('\n', ' ').strip()
				imageText = '<img id="%s" onclick="%s" style="position:fixed; left:%spx; top:%spx; z-index:%s;%s" src="data:image/gif;base64,%s">\n' %(
					obj.name,
					onclick,
					bounds[0].x * multiplyUnits,
					-bounds[0].z * multiplyUnits,
					zIndex,
					userCss,
					base64EncodedStr
				)
				imgs.append(imageText)
		for obj in previousVisibleObjects:
			obj.hide_render = False
		cameraObj.location = previousCameraLocation
		cameraObj.rotation_mode = previousCameraRotationMode
		cameraObj.rotation_euler = previousCameraRotation
		camera.type = previousCameraType
		camera.ortho_scale = previousCameraOrthoScale
		for tname in js_blocks:
			html.append('//' + tname)
			html.append(js_blocks[tname])
		html.append('</script>')
		html.append('</head>')
		html.append('<body>')
		html += imgs
		html.append('</body></html>')
		htmlText = '\n'.join(html)
		open(htmlExportPath + '/index.html', 'wb').write(htmlText.encode('utf-8'))
		if '__index__.html' not in bpy.data.texts:
			bpy.data.texts.new(name='__index__.html')
		bpy.data.texts['__index__.html'].from_string(htmlText)
		if bpy.data.worlds[0].holyserver:
			scope = globals()
			exec(bpy.data.worlds[0].holyserver.as_string(), scope, scope)
			webbrowser.open('http://localhost:8000/')
		else:
			webbrowser.open(htmlExportPath + '/index.html')
		return {'FINISHED'}

class UnrealExportButton (bpy.types.Operator):
	bl_idname = 'unreal.export'
	bl_label = 'Export To Unreal'

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		global unrealCodePath
		global childrenDict
		global unrealCodePathSuffix
		BuildTool ('UnityToUnreal')
		unrealExportPath = os.path.expanduser(context.scene.world.unrealExportPath)
		importPath = os.path.expanduser(context.scene.world.unity_project_import_path)
		if importPath != '':
			command = [ 'python3', os.path.expanduser('~/HolyBlender/UnityToUnreal.py'), 'input=' + importPath, 'output=' + unrealExportPath, 'exclude=/Library' ]
			print(command)

			subprocess.check_call(command)

		else:
			unrealCodePath = unrealExportPath
			unrealProjectName = unrealExportPath[unrealExportPath.rfind('/') + 1 :]
			unrealCodePathSuffix = '/Source/' + unrealProjectName
			unrealCodePath += unrealCodePathSuffix
			MakeFolderForFile ('/tmp/HolyBlender (Unreal Scripts)/')
			data = unrealExportPath + '\n' + bpy.data.filepath + '\n'
			for collection in bpy.data.collections:
				for obj in collection.objects:
					if obj.instance_collection == None:
						data += self.GetObjectsData(collection.objects) + '\n'
			data += '\nScenes\n'
			for scene in bpy.data.scenes:
				data += self.GetObjectsData(scene.objects) + '\n'
			data += 'Children\n'
			data += self.GetObjectsData(childrenDict) + '\n'
			data += '\nScripts'
			for obj in attachedUnrealScriptsDict:
				if len(attachedUnrealScriptsDict[obj]) > 0:
					data += '\n' + self.GetBasicObjectData(obj) + '☣️' + '☣️'.join(attachedUnrealScriptsDict[obj]) + '\n'
					for property in obj.keys():
						data += property + '☣️' + str(type(obj[property])) + '☣️' + str(obj[property]) + '☣️'
					data = data[: len(data) - 2]
					for script in attachedUnrealScriptsDict[obj]:
						for textBlock in bpy.data.texts:
							if textBlock.name == script:
								if not script.endswith('.h') and not script.endswith('.cpp') and not script.endswith('.cs'):
									script += '.cs'
								open('/tmp/HolyBlender (Unreal Scripts)/' + script, 'wb').write(textBlock.as_string().encode('utf-8'))
								break
			open('/tmp/HolyBlender Data (BlenderToUnreal)', 'wb').write(data.encode('utf-8'))
			projectFilePath = unrealExportPath + '/' + unrealProjectName + '.uproject'
			if not os.path.isdir(unrealExportPath):
				MakeFolderForFile (unrealExportPath + '/')
				bareProjectPath = os.path.expanduser('~/HolyBlender/BareUEProject')
				filesAndFolders = os.listdir(bareProjectPath)
				for fileOrFolder in filesAndFolders:
					command = 'cp -r ''' + bareProjectPath + '/' + fileOrFolder + ' ' + unrealExportPath
					print(command)

					os.system(command)

				os.rename(unrealExportPath + '/Source/BareUEProject', unrealCodePath)
				os.rename(unrealExportPath + '/BareUEProject.uproject', projectFilePath)
				command = 'cp -r ' + TEMPLATES_PATH + '/Utils.h' + ' ' + unrealCodePath + '''/Utils.h
					cp -r ''' + TEMPLATES_PATH + '/Utils.cpp' + ' ' + unrealCodePath + '/Utils.cpp'
				print(command)

				os.system(command)
				projectFileText = open(projectFilePath, 'rb').read().decode('utf-8')
				projectFileText = projectFileText.replace('BareUEProject', unrealProjectName)
				open(projectFilePath, 'wb').write(projectFileText.encode('utf-8'))
				defaultActorFilePath = unrealCodePath + '/MyActor.h'
				defaultActorFileText = open(defaultActorFilePath, 'rb').read().decode('utf-8')
				defaultActorFileText = defaultActorFileText.replace('BAREUEPROJECT', unrealProjectName.upper())
				open(defaultActorFilePath, 'wb').write(defaultActorFileText.encode('utf-8'))
				utilsFilePath = unrealCodePath + '/Utils.h'
				utilsFileText = open(utilsFilePath, 'rb').read().decode('utf-8')
				utilsFileText = utilsFileText.replace('BAREUEPROJECT', unrealProjectName.upper())
				open(utilsFilePath, 'wb').write(utilsFileText.encode('utf-8'))
				codeFilesPaths = GetAllFilePathsOfType(unrealExportPath, '.cs')
				codeFilesPaths.append(unrealCodePath + '/BareUEProject.h')
				codeFilesPaths.append(unrealCodePath + '/BareUEProject.cpp')
				for codeFilePath in codeFilesPaths:
					codeFileText = open(codeFilePath, 'rb').read().decode('utf-8')
					codeFileText = codeFileText.replace('BareUEProject', unrealProjectName)
					open(codeFilePath, 'wb').write(codeFileText.encode('utf-8'))
					os.rename(codeFilePath, codeFilePath.replace('BareUEProject', unrealProjectName))
			command = 'dotnet ' + os.path.expanduser('~/UnrealEngine/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll ') + unrealProjectName + ' Development Linux -Project="' + projectFilePath + '" -TargetType=Editor -Progress'
			if os.path.expanduser('~') == '/home/gilead':
				command = command.replace('dotnet', '/home/gilead/Downloads/dotnet-sdk-6.0.302-linux-x64/dotnet')
				command = command.replace(os.path.expanduser('~/UnrealEngine'), os.path.expanduser('~/Downloads/Linux_Unreal_Engine_5.4.3'))
			print(command)

			os.system(command)

			open('/tmp/HolyBlender Data (UnityToUnreal)', 'wb').write(''.encode('utf-8'))
			unrealEditorPath = os.path.expanduser('~/UnrealEngine/Engine/Binaries/Linux/UnrealEditor-Cmd')
			if os.path.expanduser('~') == '/home/gilead':
				unrealEditorPath = '/home/gilead/Downloads/Linux_Unreal_Engine_5.4.3/Engine/Binaries/Linux/UnrealEditor-Cmd'
			command = unrealEditorPath + ' ' + projectFilePath + ' -nullrhi -ExecutePythonScript=' + os.path.expanduser('~/HolyBlender/MakeUnrealProject.py')
			print(command)

			os.system(command)

			command = unrealEditorPath + ' ' + projectFilePath + ' -buildlighting'
			print(command)

			os.system(command)

	def GetObjectsData (self, objectGroup):
		data = 'Cameras'
		for camera in bpy.data.cameras:
			if camera.name in objectGroup.keys():
				data += '\n' + GetCameraData(camera)
		data += '\nLights'
		for light in bpy.data.lights:
			if light.name in objectGroup.keys():
				data += '\n' + GetLightData(light)
		data += '\nMeshes'
		for obj in objectGroup:
			if obj.type == 'MESH':
				ExportMesh (obj, '/tmp')
				data += '\n' + self.GetBasicObjectData(obj)
				if obj.rigid_body != None:
					data += '☣️' + str(obj.rigid_body.mass) + '☣️' + str(obj.rigid_body.linear_damping) + '☣️' + str(obj.rigid_body.angular_damping) + '☣️' + str(obj.rigid_body.enabled)
				for modifier in obj.modifiers:
					if modifier.type == 'COLLISION':
						data += '☣️True'
						break
		return data

	def GetBasicObjectData (self, obj):
		global childrenDict
		for _obj in bpy.data.objects:
			if _obj.name == obj.name:
				obj = _obj
				break
		previousObjectRotationMode = obj.rotation_mode
		obj.rotation_mode = 'QUATERNION'
		output = obj.name + '☣️' + str(obj.location * 100) + '☣️' + str(obj.rotation_quaternion) + '☣️' + str(obj.scale)
		if len(obj.children) > 0:
			for child in obj.children:
				childrenDict[child.name] = child
		obj.rotation_mode = previousObjectRotationMode
		return output

	def GetCameraData (self, camera):
		horizontalFov = False
		if camera.sensor_fit == 'HORIZONTAL':
			horizontalFov = True
		isOrthographic = False
		if camera.type == 'ORTHO':
			isOrthographic = True
		return self.GetBasicObjectData(camera) + '☣️' + str(horizontalFov) + '☣️' + str(camera.angle * (180.0 / PI)) + '☣️' + str(isOrthographic) + '☣️' + str(camera.ortho_scale) + '☣️' + str(camera.clip_start) + '☣️' + str(camera.clip_end)

	def GetLightData (self, light):
		lightType = 0
		if light.type == 'POINT':
			lightType = 1
		elif light.type == 'SPOT':
			lightType = 2
		elif lightObject.type == 'AREA':
			lightType = 3
		return self.GetBasicObjectData(light) + '☣️' + str(lightType) + '☣️' + str(light.energy * WATTS_TO_CANDELAS * 100) + '☣️' + str(light.color)

class GodotExportButton (bpy.types.Operator):
	bl_idname = 'godot.export'
	bl_label = 'Export To Godot'
	SCENE_TEMPLATE = '[gd_scene load_steps=3 format=3 uid="uid://lop2cefb4wqg"]'
	RESOURCE_TEMPLATE = '[ext_resource type="ꗈ0" uid="uid://ꗈ1" path="res://ꗈ2" id="ꗈ3"]'
	SUB_RESOURCE_TEMPLATE = '[sub_resource type="ꗈ0" id="ꗈ1"]'
	MODEL_TEMPLATE = '[node name="ꗈ0" parent="ꗈ1" instance=ExtResource("ꗈ2")]'
	TRANSFORM_TEMPLATE = 'transform = Transform3D(ꗈ0, ꗈ1, ꗈ2, ꗈ3, ꗈ4, ꗈ5, ꗈ6, ꗈ7, ꗈ8, ꗈ9, ꗈ10, ꗈ11)'
	NODE_TEMPLATE = '[node name="ꗈ0" type="ꗈ1" parent="ꗈ2"]'
	godotExportPath = ''
	resources = ''
	nodes = ''
	idIndex = 0
	exportedObjs = []

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		self.godotExportPath = os.path.expanduser(context.scene.world.godotExportPath)
		if not os.path.isdir(self.godotExportPath):
			MakeFolderForFile (os.path.join(self.godotExportPath, ''))
		importPath = os.path.expanduser(context.scene.world.unity_project_import_path)
		self.idIndex = 0
		if importPath != '':
			print('Exporting from Unity to Godot doesn\'t work yet')
		else:
			
			os.system('mkdir ' + self.godotExportPath + '\ncd ' + self.godotExportPath + '\ntouch project.godot')
			
			MakeFolderForFile (os.path.join(self.godotExportPath, 'Scenes', ''))
			MakeFolderForFile (os.path.join(self.godotExportPath, 'Scripts', ''))
			CopyFile (os.path.join(GODOT_SCRIPTS_PATH, 'AddMeshCollision.gd'), os.path.join(self.godotExportPath, 'Scripts', 'AddMeshCollision.gd'))
			CopyFile (os.path.join(GODOT_SCRIPTS_PATH, 'SendAndRecieveServerEvents.gd'), os.path.join(self.godotExportPath, 'Scripts', 'SendAndRecieveServerEvents.gd'))
			self.resources = ''
			self.nodes = ''
			self.exportedObjs = []
			for obj in bpy.data.objects:
				if obj not in self.exportedObjs:
					self.MakeObject (obj)
			id = self.GetId(7)
			resource = self.RESOURCE_TEMPLATE
			resource = resource.replace(REPLACE_INDICATOR + '0', 'Script')
			resource = resource.replace(REPLACE_INDICATOR + '1', self.GetId(13))
			resource = resource.replace(REPLACE_INDICATOR + '2', os.path.join('Scripts', 'SendAndRecieveServerEvents.gd'))
			resource = resource.replace(REPLACE_INDICATOR + '3', id)
			self.resources += resource
			node3d = self.NODE_TEMPLATE
			node3d = node3d.replace(REPLACE_INDICATOR + '0', 'Send And Recieve Click Events')
			node3d = node3d.replace(REPLACE_INDICATOR + '1', 'Node3D')
			node3d = node3d.replace(REPLACE_INDICATOR + '2', '.')
			node3d += '\nscript = ExtResource("' + id + '")'
			self.nodes += node3d
			sceneText = self.SCENE_TEMPLATE
			sceneText += '\n' + self.resources + '\n[node name="' + bpy.context.scene.name + '" type="Node3D"]\n' + self.nodes
			open(os.path.join(self.godotExportPath, 'Scenes', bpy.context.scene.name + '.tscn'), 'wb').write(sceneText.encode('utf-8'))
			
			os.system('flatpak run org.godotengine.Godot ' + os.path.join(self.godotExportPath, 'project.godot'))

	def MakeObject (self, obj):
		global attachedGodotScriptsDict
		for obj2 in bpy.data.objects:
			if obj in obj2.children and obj2 not in self.exportedObjs:
				self.MakeObject (obj2)
		if obj.type == 'MESH':
			fileExportFolder = os.path.join(self.godotExportPath, 'Art', 'Models')
			fileExportPath = os.path.join(fileExportFolder, '')
			MakeFolderForFile (fileExportPath)
			fileExportPath = ExportMesh(obj, fileExportFolder)
			id = self.GetId(7)
			resource = self.RESOURCE_TEMPLATE
			resource = resource.replace(REPLACE_INDICATOR + '0', 'PackedScene')
			resource = resource.replace(REPLACE_INDICATOR + '1', self.GetId(13))
			resource = resource.replace(REPLACE_INDICATOR + '2', fileExportPath.replace(os.path.join(self.godotExportPath, ''), ''))
			resource = resource.replace(REPLACE_INDICATOR + '3', id)
			self.resources += resource + '\n'
			parentPath = self.GetParentPath(obj)
			if obj.rigid_body != None:
				rigidBody = self.NODE_TEMPLATE
				for modifier in obj.modifiers:
					if modifier.type == 'COLLISION':
						rigidBody = self.NODE_TEMPLATE[: -1] + 'node_paths=PackedStringArray("meshInstance")]'
						scriptId = self.GetId(7)
						resource = self.RESOURCE_TEMPLATE
						resource = resource.replace(REPLACE_INDICATOR + '0', 'Script')
						resource = resource.replace(REPLACE_INDICATOR + '1', self.GetId(13))
						resource = resource.replace(REPLACE_INDICATOR + '2', os.path.join('Scripts', 'AddMeshCollision.gd'))
						resource = resource.replace(REPLACE_INDICATOR + '3', scriptId)
						self.resources += resource + '\n'
						rigidBody += '\nscript = ExtResource("' + scriptId + '")'
						meshInstancePath = obj.name + '/' + obj.name
						rigidBody += '\nmeshInstance = NodePath("' + meshInstancePath + '")'
						break
				rigidBodyName = obj.name + ' (RigidBody3D)'
				rigidBodyParentPath = parentPath.replace(rigidBodyName + '/', '')
				if rigidBodyParentPath == '':
					rigidBodyParentPath = '.'
				rigidBody = rigidBody.replace(REPLACE_INDICATOR + '0', rigidBodyName)
				rigidBody = rigidBody.replace(REPLACE_INDICATOR + '1', 'RigidBody3D')
				rigidBody = rigidBody.replace(REPLACE_INDICATOR + '2', rigidBodyParentPath)
				rigidBody += '\nmass = ' + str(obj.rigid_body.mass)
				rigidBody += '\nlinear_damp_mode = 1'
				rigidBody += '\nlinear_damp = ' + str(obj.rigid_body.linear_damping)
				rigidBody += '\nangular_damp_mode = 1'
				rigidBody += '\nangular_damp = ' + str(obj.rigid_body.angular_damping)
				rigidBody += '\nfreeze = ' + str(int(not obj.rigid_body.enabled))
				self.nodes += rigidBody + '\n'
			model = self.MODEL_TEMPLATE
			model = model.replace(REPLACE_INDICATOR + '0', obj.name)
			model = model.replace(REPLACE_INDICATOR + '1', parentPath)
			model = model.replace(REPLACE_INDICATOR + '2', id)
			model += '\n' + self.GetTransformText(obj)
			self.nodes += model + '\n'
			self.MakeClickableChild (obj)
		elif obj.type == 'LIGHT':
			light = self.NODE_TEMPLATE
			light = light.replace(REPLACE_INDICATOR + '0', obj.name)
			lightObj = None
			for _light in bpy.data.lights:
				if _light.name == obj.name:
					lightObj = _light
					break
			if lightObj.type == 'SUN':
				light = light.replace(REPLACE_INDICATOR + '1', 'DirectionalLight3D')
			elif lightObj.type == 'POINT':
				light = light.replace(REPLACE_INDICATOR + '1', 'OmniLight3D')
			elif lightObj.type == 'SPOT':
				light = light.replace(REPLACE_INDICATOR + '1', 'SpotLight3D')
			else:# elif lightObject.type == 'AREA':
				print('Area lights are not supported in Godot')
				return
			light = light.replace(REPLACE_INDICATOR + '2', self.GetParentPath(obj))
			if lightObj.type == 'POINT':
				light += '\nomni_range = ' + str(lightObj.cutoff_distance)
			elif lightObj.type == 'SPOT':
				light += '\nspot_range = ' + str(lightObj.cutoff_distance)
				light += '\nspot_angle = ' + str(lightObj.spot_size)
			light += '\nlight_energy = ' + str(lightObj.energy * WATTS_TO_CANDELAS)
			light += '\nlight_color = ' + 'Color(' + str(lightObj.color[0]) + ', ' + str(lightObj.color[1]) + ', ' + str(lightObj.color[2]) + ', 1)'
			light += '\n' + self.GetTransformText(obj)
			self.nodes += light + '\n'
		elif obj.type == 'CAMERA':
			camera = self.NODE_TEMPLATE
			camera = camera.replace(REPLACE_INDICATOR + '0', obj.name)
			camera = camera.replace(REPLACE_INDICATOR + '1', 'Camera3D')
			camera = camera.replace(REPLACE_INDICATOR + '2', self.GetParentPath(obj))
			cameraObj = None
			for _camera in bpy.data.cameras:
				if _camera.name == obj.name:
					cameraObj = _camera
					break
			if cameraObj.type == 'ORTHO':
				camera += '\nprojection = 1'
				camera += '\nsize = ' + str(cameraObj.ortho_scale)
			else:
				camera += '\nprojection = 0'
				camera += '\nfov = ' + str(math.degrees(cameraObj.angle))
			camera += '\nnear = ' + str(cameraObj.clip_start)
			camera += '\nfar = ' + str(cameraObj.clip_end)
			camera += '\n' + self.GetTransformText(obj)
			self.nodes += camera + '\n'
		attachedScripts = attachedGodotScriptsDict.get(obj, [])
		for attachedScript in attachedScripts:
			script = attachedScript
			if not attachedScript.endswith('.gd'):
				script += '.gd'
			for textBlock in bpy.data.texts:
				if textBlock.name == attachedScript:
					open(os.path.join(self.godotExportPath, 'Scripts', script), 'wb').write(textBlock.as_string().encode('utf-8'))
					break
			id = self.GetId(7)
			resource = self.RESOURCE_TEMPLATE
			resource = resource.replace(REPLACE_INDICATOR + '0', 'Script')
			resource = resource.replace(REPLACE_INDICATOR + '1', self.GetId(13))
			resource = resource.replace(REPLACE_INDICATOR + '2', os.path.join('Scripts', script))
			resource = resource.replace(REPLACE_INDICATOR + '3', id)
			self.resources += resource + '\n'
			self.nodes += '\nscript = ExtResource("' + id + '")'
		self.exportedObjs.append(obj)
	
	def GetTransformText (self, obj):
		transform = self.TRANSFORM_TEMPLATE
		location = obj.location
		if obj.type == 'MESH':
			location = mathutils.Vector((0, 0, 0))
		previousObjectRotationMode = obj.rotation_mode
		obj.rotation_mode = 'XYZ'
		size = mathutils.Vector((obj.scale.x, obj.scale.z, obj.scale.y))
		matrix = mathutils.Matrix.LocRotScale(mathutils.Vector((0, 0, 0)), obj.rotation_euler, size)
		right = mathutils.Vector((1, 0, 0)) @ matrix
		up = mathutils.Vector((0, 0, 1)) @ matrix
		forward = mathutils.Vector((0, 1, 0)) @ matrix
		obj.rotation_mode = previousObjectRotationMode
		transform = transform.replace(REPLACE_INDICATOR + '10', str(location.z))
		transform = transform.replace(REPLACE_INDICATOR + '11', str(-location.y))
		transform = transform.replace(REPLACE_INDICATOR + '0', str(right.x))
		transform = transform.replace(REPLACE_INDICATOR + '1', str(right.y))
		transform = transform.replace(REPLACE_INDICATOR + '2', str(right.z))
		transform = transform.replace(REPLACE_INDICATOR + '3', str(up.x))
		transform = transform.replace(REPLACE_INDICATOR + '4', str(up.y))
		transform = transform.replace(REPLACE_INDICATOR + '5', str(up.z))
		transform = transform.replace(REPLACE_INDICATOR + '6', str(forward.x))
		transform = transform.replace(REPLACE_INDICATOR + '7', str(forward.y))
		transform = transform.replace(REPLACE_INDICATOR + '8', str(forward.z))
		transform = transform.replace(REPLACE_INDICATOR + '9', str(location.x))
		return transform
	
	def GetParentPath (self, obj):
		output = ''
		parent = obj
		if obj.rigid_body != None:
			output = obj.name + ' (RigidBody3D)/'
		for obj2 in bpy.data.objects:
			if parent in obj2.children:
				parent = obj2
				if obj2.rigid_body != None:
					output += obj2.name + ' (RigidBody3D)/'
				output += obj2.name + '/'
		if output == '':
			output = '.'
		return output

	def GetId (self, length : int):
		output = '1'
		for i in range(1, length):
			output += '0'
		output = str(int(output) + self.idIndex)
		self.idIndex += 1
		return output

	def MakeClickableChild (self, obj):
		parentPath = self.GetParentPath(obj)
		rigidBody = self.NODE_TEMPLATE[: -1] + 'node_paths=PackedStringArray("meshInstance")]'
		rigidBody = rigidBody.replace(REPLACE_INDICATOR + '0', obj.name + ' (Clickable)')
		rigidBody = rigidBody.replace(REPLACE_INDICATOR + '1', 'RigidBody3D')
		rigidBody = rigidBody.replace(REPLACE_INDICATOR + '2', parentPath + obj.name)
		rigidBody += '\nfreeze = true'
		rigidBody += '\ncollision_layer = 2147483648'
		rigidBody += '\ncollision_mask = 0'
		id = self.GetId(7)
		rigidBody += '\nscript = ExtResource("' + id + '")'
		meshInstancePath = '../' + obj.name
		rigidBody += '\nmeshInstance = NodePath("' + meshInstancePath + '")'
		self.nodes += rigidBody + '\n'
		resource = self.RESOURCE_TEMPLATE
		resource = resource.replace(REPLACE_INDICATOR + '0', 'Script')
		resource = resource.replace(REPLACE_INDICATOR + '1', self.GetId(13))
		resource = resource.replace(REPLACE_INDICATOR + '2', os.path.join('Scripts', 'AddMeshCollision.gd'))
		resource = resource.replace(REPLACE_INDICATOR + '3', id)
		self.resources += resource + '\n'

class BevyExportButton (bpy.types.Operator):
	bl_idname = 'bevy.export'
	bl_label = 'Export To Bevy'

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		bevyExportPath = os.path.expanduser(context.scene.world.bevy_project_path)
		if not os.path.isdir(bevyExportPath):
			MakeFolderForFile (bevyExportPath + '/')
		importPath = os.path.expanduser(context.scene.world.unity_project_import_path)
		if importPath != '':
			BuildTool ('UnityToBevy')
			command = [ 'python3', os.path.expanduser('~/HolyBlender/UnityToBevy.py'), 'input=' + importPath, 'output=' + bevyExportPath, 'exclude=/Library', 'webgl' ]
			print(command)

			subprocess.check_call(command)

		else:
			data = bevyExportPath
			for obj in attachedBevyScriptsDict:
				data += '\n' + obj.name + '☢️' + '☣️'.join(attachedBevyScriptsDict[obj])
			open('/tmp/HolyBlender Data (BlenderToBevy)', 'wb').write(data.encode('utf-8'))
			import MakeBevyBlenderApp as makeBevyBlenderApp
			makeBevyBlenderApp.Do (attachedBevyScriptsDict)
			# webbrowser.open('http://localhost:1334')

class UnityExportButton (bpy.types.Operator):
	bl_idname = 'unity.export'
	bl_label = 'Export To Unity'
	INIT_YAML_TEXT = '''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:'''
	MATERIAL_TEMPLATE = '    - {fileID: ꗈ0, guid: ꗈ1, type: 2}'
	COMPONENT_TEMPLATE = '    - component: {fileID: ꗈ}'
	CHILD_TRANSFORM_TEMPLATE = '    - {fileID: ꗈ}'
	SCENE_ROOT_TEMPLATE = CHILD_TRANSFORM_TEMPLATE
	GAME_OBJECT_TEMPLATE = '''--- !u!1 &ꗈ0
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  serializedVersion: 6
  m_Component:
  - component: {fileID: ꗈ1}
ꗈ2
  m_Layer: ꗈ3
  m_Name: ꗈ4
  m_TagString: ꗈ5
  m_Icon: {fileID: 0}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1'''
	TRANSFORM_TEMPLATE = '''--- !u!4 &ꗈ0
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  serializedVersion: 2
  m_LocalRotation: {x: ꗈ2, y: ꗈ3, z: ꗈ4, w: ꗈ5}
  m_LocalPosition: {x: ꗈ6, y: ꗈ7, z: ꗈ8}
  m_LocalScale: {x: ꗈ9, y: ꗈ10, z: ꗈ11}
  m_ConstrainProportionsScale: 0
  m_Children: ꗈ12
  m_Father: {fileID: ꗈ13}
  m_LocalEulerAnglesHint: {x: 0, y: 0, z: 0}'''
	LIGHT_TEMPLATE = '''--- !u!108 &ꗈ0
Light:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  m_Enabled: 1
  serializedVersion: 11
  m_Type: ꗈ2
  m_Color: {r: ꗈ3, g: ꗈ4, b: ꗈ5, a: 1}
  m_Intensity: ꗈ6
  m_Range: ꗈ7
  m_SpotAngle: ꗈ8
  m_InnerSpotAngle: ꗈ9
  m_CookieSize: 10
  m_Shadows:
  m_Type: 0
  m_Resolution: -1
  m_CustomResolution: -1
  m_Strength: 1
  m_Bias: 0.05
  m_NormalBias: 0.4
  m_NearPlane: 0.2
  m_CullingMatrixOverride:
    e00: 1
    e01: 0
    e02: 0
    e03: 0
    e10: 0
    e11: 1
    e12: 0
    e13: 0
    e20: 0
    e21: 0
    e22: 1
    e23: 0
    e30: 0
    e31: 0
    e32: 0
    e33: 1
  m_UseCullingMatrixOverride: 0
  m_Cookie: {fileID: 0}
  m_DrawHalo: 0
  m_Flare: {fileID: 0}
  m_RenderMode: 0
  m_CullingMask:
  serializedVersion: 2
  m_Bits: 4294967295
  m_RenderingLayerMask: 1
  m_Lightmapping: 4
  m_LightShadowCasterMode: 0
  m_AreaSize: {x: 1, y: 1}
  m_BounceIntensity: 1
  m_ColorTemperature: 6570
  m_UseColorTemperature: 0
  m_BoundingSphereOverride: {x: 0, y: 0, z: 0, w: 0}
  m_UseBoundingSphereOverride: 0
  m_UseViewFrustumForShadowCasterCull: 1
  m_ShadowRadius: 0
  m_ShadowAngle: 0'''
	SCRIPT_TEMPLATE = '''--- !u!114 &ꗈ0
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {fileID: 11500000, guid: ꗈ2, type: 3}'''
	MESH_FILTER_TEMPLATE = '''--- !u!33 &ꗈ0
MeshFilter:
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  m_Mesh: {fileID: ꗈ2, guid: ꗈ3, type: 3}'''
	MESH_RENDERER_TEMPLATE = '''--- !u!23 &ꗈ0
MeshRenderer:
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  m_Materials:
ꗈ2'''
	MESH_COLLIDER_TEMPLATE = '''--- !u!64 &ꗈ0
MeshCollider:
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  m_Material: {fileID: 0}
  m_IsTrigger: ꗈ2
  m_Convex: ꗈ3
  m_Mesh: {fileID: ꗈ4, guid: ꗈ5, type: 3}'''
	RIGIDBODY_TEMPLATE = '''--- !u!54 &ꗈ0
Rigidbody:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  serializedVersion: 4
  m_Mass: ꗈ2
  m_Drag: ꗈ3
  m_AngularDrag: ꗈ4
  m_CenterOfMass: {x: 0, y: 0, z: 0}
  m_InertiaTensor: {x: 1, y: 1, z: 1}
  m_InertiaRotation: {x: 0, y: 0, z: 0 w: 1}
  m_IncludeLayers:
    serializedVersion: 2
    m_Bits: 0
  m_ExcludeLayers:
    serializedVersion: 2
    m_Bits: 0
  m_ImplicitCom: 1
  m_ImplicitTensor: 1
  m_UseGravity: ꗈ5
  m_IsKinematic: ꗈ6
  m_Interpolate: ꗈ7
  m_Constraints: ꗈ8
  m_CollisionDetection: ꗈ9'''
	CAMERA_TEMPLATE = '''--- !u!20 &ꗈ0
Camera:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  m_Enabled: 1
  serializedVersion: 2
  m_ClearFlags: 1
  m_BackGroundColor: {r: 0.19215687, g: 0.3019608, b: 0.4745098, a: 0}
  m_projectionMatrixMode: 1
  m_GateFitMode: 2
  m_FOVAxisMode: ꗈ2
  m_Iso: 200
  m_ShutterSpeed: 0.005
  m_Aperture: 16
  m_FocusDistance: 10
  m_FocalLength: 50
  m_BladeCount: 5
  m_Curvature: {x: 2, y: 11}
  m_BarrelClipping: 0.25
  m_Anamorphism: 0
  m_SensorSize: {x: 36, y: 24}
  m_LensShift: {x: 0, y: 0}
  m_NormalizedViewPortRect:
    serializedVersion: 2
    x: 0
    y: 0
    width: 1
    height: 1
  near clip plane: ꗈ3
  far clip plane: ꗈ4
  field of view: ꗈ5
  orthographic: ꗈ6
  orthographic size: ꗈ7
  m_Depth: 0
  m_CullingMask:
  serializedVersion: 2
  m_Bits: 4294967295
  m_RenderingPath: -1
  m_TargetTexture: {fileID: 0}
  m_TargetDisplay: 0
  m_TargetEye: 3
  m_HDR: 1
  m_AllowMSAA: 1
  m_AllowDynamicResolution: 0
  m_ForceIntoRT: 0
  m_OcclusionCulling: 1
  m_StereoConvergence: 10
  m_StereoSeparation: 0.022'''
	SPRITE_RENDERER_TEMPLATE = '''--- !u!212 &ꗈ0
SpriteRenderer:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: ꗈ1}
  m_Enabled: 1
  m_CastShadows: 0
  m_ReceiveShadows: 0
  m_DynamicOccludee: 1
  m_StaticShadowCaster: 0
  m_MotionVectors: 1
  m_LightProbeUsage: 1
  m_ReflectionProbeUsage: 1
  m_RayTracingMode: 0
  m_RayTraceProcedural: 0
  m_RayTracingAccelStructBuildFlagsOverride: 0
  m_RayTracingAccelStructBuildFlags: 1
  m_SmallMeshCulling: 1
  m_RenderingLayerMask: 1
  m_RendererPriority: 0
  m_Materials:
  - {fileID: 10754, guid: 0000000000000000f000000000000000, type: 0}
  m_StaticBatchInfo:
    firstSubMesh: 0
    subMeshCount: 0
  m_StaticBatchRoot: {fileID: 0}
  m_ProbeAnchor: {fileID: 0}
  m_LightProbeVolumeOverride: {fileID: 0}
  m_ScaleInLightmap: 1
  m_ReceiveGI: 1
  m_PreserveUVs: 0
  m_IgnoreNormalsForChartDetection: 0
  m_ImportantGI: 0
  m_StitchLightmapSeams: 1
  m_SelectedEditorRenderState: 0
  m_MinimumChartSize: 4
  m_AutoUVMaxDistance: 0.5
  m_AutoUVMaxAngle: 89
  m_LightmapParameters: {fileID: 0}
  m_SortingLayerID: ꗈ2
  m_SortingLayer: ꗈ3
  m_SortingOrder: ꗈ4
  m_Sprite: {fileID: 0, guid: ꗈ5, type: 3}
  m_Color: {r: 1, g: 1, b: 1, a: 1}
  m_FlipX: 0
  m_FlipY: 0
  m_DrawMode: 0
  m_Size: {x: 0, y: 0}
  m_AdaptiveModeThreshold: 0.5
  m_SpriteTileMode: 0
  m_WasSpriteAssigned: 1
  m_MaskInteraction: 0
  m_SpriteSortPoint: 0'''
	SPRITE_META_TEMPLATE = '''fileFormatVersion: 2
guid: ꗈ0
TextureImporter:
  internalIDToNameTable:
  - first:
      213: 0
    second: ꗈ1_0
  externalObjects: {}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 1
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 16384
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 2
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {x: 0.5, y: 0.5}
  spritePixelsToUnits: 100
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 16384
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: Win64
    maxTextureSize: 16384
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: Linux64
    maxTextureSize: 16384
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: Standalone
    maxTextureSize: 16384
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: Android
    maxTextureSize: 16384
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites:
    - serializedVersion: 2
      name: ꗈ1_0
      rect:
        serializedVersion: 2
        x: 0
        y: 0
        width: 242
        height: 188
      alignment: 0
      pivot: {x: 0, y: 0}
      border: {x: 0, y: 0, z: 0, w: 0}
      customData: 
      outline: []
      physicsShape: []
      tessellationDetail: -1
      bones: []
      spriteID: 85166db83dab01790800000000000000
      internalID: 0
      vertices: []
      indices: 
      edges: []
      weights: []
    outline: []
    customData: 
    physicsShape: []
    bones: []
    spriteID: 
    internalID: 0
    vertices: []
    indices: 
    edges: []
    weights: []
    secondaryTextures: []
    spriteCustomMetadata:
      entries: []
    nameFileIdTable:
      ꗈ1_0: 0
  mipmapLimitGroupName: 
  pSDRemoveMatte: 0
  userData: 
  assetBundleName: 
  assetBundleVariant: '''
	PREFAB_INSTANCE_TEMPLATE = '''--- !u!1001 &ꗈ0
PrefabInstance:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Modification:
    serializedVersion: 3
    m_TransformParent: {fileID: ꗈ1}
    m_Modifications:
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalPosition.x
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalPosition.y
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalPosition.z
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalRotation.w
      value: 1
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalRotation.x
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalRotation.y
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalRotation.z
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalEulerAnglesHint.x
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalEulerAnglesHint.y
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
      propertyPath: m_LocalEulerAnglesHint.z
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 8879364713982270700, guid: ꗈ2, type: 3}
      propertyPath: m_Name
      value: ꗈ3
      objectReference: {fileID: 0}
	ꗈ4
    m_RemovedComponents: ꗈ5
    m_RemovedGameObjects: ꗈ6
    m_AddedGameObjects: ꗈ7
    m_AddedComponents: ꗈ8
  m_SourcePrefab: {fileID: 100100000, guid: ꗈ2, type: 3}
--- !u!4 &ꗈ9 stripped
Transform:
  m_CorrespondingSourceObject: {fileID: 5125873004793848012, guid: ꗈ2, type: 3}
  m_PrefabInstance: {fileID: ꗈ0}
  m_PrefabAsset: {fileID: 0}'''
	gameObjectsAndComponentsText = ''
	transformIds = []
	componentIds = []
	projectExportPath = ''
	unityVersionPath = ''
	lastId = 5

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		self.lastId = 5
		self.projectExportPath = os.path.expanduser(context.scene.world.unity_project_export_path)
		if not os.path.isdir(self.projectExportPath):
			os.mkdir(self.projectExportPath)
		meshesDict = {}
		for mesh in bpy.data.meshes:
			meshesDict[mesh.name] = []
		for obj in bpy.context.scene.objects:
			if obj.type == 'MESH' and obj.data.name in meshesDict:
				meshesDict[obj.data.name].append(obj.name)
				fileExportFolder = os.path.join(self.projectExportPath, 'Assets', 'Art', 'Models')
				fileExportPath = os.path.join(fileExportFolder, '')
				MakeFolderForFile (fileExportPath)
				# prevoiusObjectSize = obj.scale
				# obj.scale *= 100
				fileExportPath = ExportMesh(obj, fileExportFolder)
				# obj.scale = prevoiusObjectSize
				for materialSlot in obj.material_slots:
					fileExportPath = self.projectExportPath + '/Assets/Art/Materials/' + materialSlot.material.name + '.mat'
					MakeFolderForFile (fileExportPath)
					material = open(os.path.expanduser('~/HolyBlender/Templates/Material.mat'), 'rb').read().decode('utf-8')
					material = material.replace(REPLACE_INDICATOR + '0', materialSlot.material.name)
					materialColor = materialSlot.material.diffuse_color
					material = material.replace(REPLACE_INDICATOR + '1', str(materialColor[0]))
					material = material.replace(REPLACE_INDICATOR + '2', str(materialColor[1]))
					material = material.replace(REPLACE_INDICATOR + '3', str(materialColor[2]))
					material = material.replace(REPLACE_INDICATOR + '4', str(materialColor[3]))
					open(fileExportPath, 'wb').write(material.encode('utf-8'))
			elif obj.type == 'EMPTY' and obj.empty_display_type == 'IMAGE':
				spritePath = obj.data.filepath
				spritePath = os.path.expanduser('~') + spritePath[1 :]
				spriteName = spritePath[spritePath.rfind('/') + 1 :]
				newSpritePath = os.path.join(self.projectExportPath, 'Assets', 'Art', 'Textures', spriteName)
				MakeFolderForFile (newSpritePath)
				sprite = open(spritePath, 'rb').read()
				open(newSpritePath, 'wb').write(sprite)
		unityVersionsPath = os.path.expanduser('~/Unity/Hub/Editor')
		self.unityVersionPath = ''
		if os.path.isdir(unityVersionsPath):
			unityVersions = os.listdir(unityVersionsPath)
			for unityVersion in unityVersions:
				self.unityVersionPath = unityVersionsPath + '/' + unityVersion + '/Editor/Unity'
				if os.path.isfile(self.unityVersionPath):
					self.unityVersionPath = self.unityVersionPath
					break
		if self.unityVersionPath != '':
			MakeFolderForFile (os.path.join(self.projectExportPath, 'Assets', 'Editor', ''))
			MakeFolderForFile (os.path.join(self.projectExportPath, 'Assets', 'Scripts', ''))
			CopyFile (os.path.join(UNITY_SCRIPTS_PATH, 'GetUnityProjectInfo.cs'), os.path.join(self.projectExportPath, 'Assets', 'Editor', 'GetUnityProjectInfo.cs'))
			CopyFile (os.path.join(EXTENSIONS_PATH, 'SystemExtensions.cs'), os.path.join(self.projectExportPath, 'Assets', 'Scripts', 'SystemExtensions.cs'))
			CopyFile (os.path.join(EXTENSIONS_PATH, 'StringExtensions.cs'), os.path.join(self.projectExportPath, 'Assets', 'Scripts', 'StringExtensions.cs'))
			data = ''
			for obj in bpy.data.objects:
				previousObjectRotationMode = obj.rotation_mode 
				obj.rotation_mode = 'XYZ'
				rotation = obj.rotation_euler
				obj.rotation_mode = previousObjectRotationMode
				yDegrees = math.degrees(rotation.z) + 180
				if obj.type == 'CAMERA':
					yDegrees *= -1
				data += obj.name + ', ' + str(math.degrees(rotation.x) + 90) + ', ' + str(yDegrees) + ', ' + str(math.degrees(rotation.y) + 180) + '\n'
			open(os.path.join('/tmp', 'HolyBlender Data (BlenderToUnity)'), 'wb').write(data.encode('utf-8'))
			command = self.unityVersionPath + ' -quit -createProject ' + self.projectExportPath + ' -executeMethod GetUnityProjectInfo.Do ' + self.projectExportPath
			print(command)
			
			subprocess.check_call(command.split())

		scenePath = bpy.data.filepath.replace('.blend', '.unity')
		scenePath = scenePath[scenePath.rfind('/') + 1 :]
		scenesFolderPath = self.projectExportPath + '/Assets/Scenes'
		if not os.path.isdir(scenesFolderPath):
			os.mkdir(scenesFolderPath)
		if scenePath == '':
			scenePath = 'Test.unity'
		scenePath = scenesFolderPath + '/' + scenePath
		sceneTemplateText = open(os.path.expanduser('~/HolyBlender/Templates/Scene.unity'), 'rb').read().decode('utf-8')
		prefabsPath = os.path.join(self.projectExportPath, 'Assets', 'Prefabs')
		MakeFolderForFile (os.path.join(prefabsPath, ''))
		for collection in bpy.data.collections:
			self.gameObjectsAndComponentsText = ''
			self.MakeObject (obj)
			prefab = self.INIT_YAML_TEXT
			for gameObjectOrComponentText in self.gameObjectsAndComponentsText:
				prefab += '\n' + gameObjectOrComponentText
			open(os.path.join(prefabsPath, collection.name), 'w').write(prefab)
		self.gameObjectsAndComponentsText = ''
		self.transformIds = []
		for obj in bpy.data.objects:
			shouldMakeObject = True
			for obj2 in bpy.data.objects:
				if obj in obj2.children:
					shouldMakeObject = False
					break
			if shouldMakeObject:
				self.MakeObject (obj)
		scriptsFolder = os.path.join(self.projectExportPath, 'Assets', 'Scripts')
		MakeFolderForFile (os.path.join(self.projectExportPath, 'Assets', 'Scripts', ''))
		sendAndRecieveServerEventsScriptPath = os.path.join(scriptsFolder, 'SendAndRecieveServerEvents.cs')
		CopyFile (os.path.join(UNITY_SCRIPTS_PATH, 'SendAndRecieveServerEvents.cs'), sendAndRecieveServerEventsScriptPath)
		gameObjectIdAndTransformId = self.MakeEmptyObject('Send And Recieve Server Events')
		script = self.SCRIPT_TEMPLATE
		sendAndRecieveServerEventsScriptMetaPath = sendAndRecieveServerEventsScriptPath + '.meta'
		scriptGuid = GetGuid(sendAndRecieveServerEventsScriptMetaPath)
		open(sendAndRecieveServerEventsScriptMetaPath, 'w').write('guid: ' + scriptGuid)
		script = script.replace(REPLACE_INDICATOR + '0', str(self.lastId))
		script = script.replace(REPLACE_INDICATOR + '1', str(gameObjectIdAndTransformId[0]))
		script = script.replace(REPLACE_INDICATOR + '2', scriptGuid)
		self.gameObjectsAndComponentsText += script + '\n'
		self.componentIds.append(self.lastId)
		sceneRootsText = ''
		for transformId in self.transformIds:
			sceneRoot = self.SCENE_ROOT_TEMPLATE
			sceneRoot = sceneRoot.replace(REPLACE_INDICATOR, str(transformId))
			sceneRootsText += sceneRoot + '\n'
		sceneText = sceneTemplateText.replace(REPLACE_INDICATOR + '0', self.gameObjectsAndComponentsText)
		sceneText = sceneText.replace(REPLACE_INDICATOR + '1', sceneRootsText)
		open(scenePath, 'wb').write(sceneText.encode('utf-8'))
		if self.unityVersionPath != '':
			command = [ self.unityVersionPath, '-createProject', self.projectExportPath ]
			
			subprocess.check_call(command)

	def MakeEmptyObject (self, name : str, layer = 0, parentTransformId = 0) -> (int, int):
		gameObject = self.GAME_OBJECT_TEMPLATE
		gameObject = gameObject.replace(REPLACE_INDICATOR + '0', str(self.lastId))
		gameObject = gameObject.replace(REPLACE_INDICATOR + '1', str(self.lastId + 1))
		gameObject = gameObject.replace(REPLACE_INDICATOR + '3', str(layer))
		gameObject = gameObject.replace(REPLACE_INDICATOR + '4', name)
		gameObject = gameObject.replace(REPLACE_INDICATOR + '5', 'Untagged')
		self.gameObjectsAndComponentsText += gameObject + '\n'
		gameObjectId = self.lastId
		self.lastId += 1
		transform = self.TRANSFORM_TEMPLATE
		transform = transform.replace(REPLACE_INDICATOR + '10', '1')
		transform = transform.replace(REPLACE_INDICATOR + '11', '1')
		transform = transform.replace(REPLACE_INDICATOR + '12', '[]')
		transform = transform.replace(REPLACE_INDICATOR + '13', str(parentTransformId))
		transform = transform.replace(REPLACE_INDICATOR + '0', str(self.lastId))
		transform = transform.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
		transform = transform.replace(REPLACE_INDICATOR + '2', '0')
		transform = transform.replace(REPLACE_INDICATOR + '3', '0')
		transform = transform.replace(REPLACE_INDICATOR + '4', '0')
		transform = transform.replace(REPLACE_INDICATOR + '5', '1')
		transform = transform.replace(REPLACE_INDICATOR + '6', '0')
		transform = transform.replace(REPLACE_INDICATOR + '7', '0')
		transform = transform.replace(REPLACE_INDICATOR + '8', '0')
		transform = transform.replace(REPLACE_INDICATOR + '9', '1')
		self.gameObjectsAndComponentsText += transform + '\n'
		self.transformIds.append(self.lastId)
		self.lastId += 1
		return (gameObjectId, self.lastId - 1)

	def MakeObject (self, obj, parentTransformId = 0) -> int:
		self.componentIds = []
		tag = 'Untagged'
		if obj.type == 'CAMERA':
			tag = 'MainCamera'
		gameObject = self.GAME_OBJECT_TEMPLATE
		gameObject = gameObject.replace(REPLACE_INDICATOR + '0', str(self.lastId))
		gameObject = gameObject.replace(REPLACE_INDICATOR + '1', str(self.lastId + 1))
		gameObject = gameObject.replace(REPLACE_INDICATOR + '3', '0')
		gameObject = gameObject.replace(REPLACE_INDICATOR + '4', obj.name)
		gameObject = gameObject.replace(REPLACE_INDICATOR + '5', tag)
		self.gameObjectsAndComponentsText += gameObject + '\n'
		gameObjectId = self.lastId
		self.lastId += 1
		myTransformId = self.lastId
		children = ''
		for childObj in obj.children:
			transformId = self.MakeObject(child, self.lastId)
			children += '\n' + self.CHILD_TRANSFORM_TEMPLATE.replace(REPLACE_INDICATOR, transformId)
		meshFileId = '10202'
		meshGuid = ''
		dataText = open('/tmp/HolyBlender Data (BlenderToUnity)', 'rb').read().decode('utf-8')
		if obj.type == 'MESH':
			filePath = self.projectExportPath + '/Assets/Art/Models/' + obj.name + '.fbx.meta'
			meshGuid = GetGuid(filePath)
			open(filePath, 'w').write('guid: ' + meshGuid)
			if self.unityVersionPath != '':
				meshDatas = dataText.split('\n')[0]
				fileIdIndicator = '-' + self.projectExportPath + '/Assets/Art/Models/' + obj.name + '.fbx'
				indexOfFile = meshDatas.find(fileIdIndicator)
				indexOfFileId = indexOfFile + len(fileIdIndicator) + 1
				indexOfEndOfFileId = meshDatas.find(' ', indexOfFileId)
				meshFileId = meshDatas[indexOfFileId : indexOfEndOfFileId]
			self.lastId += 1
			gameObjectIdAndTransformId = self.MakeClickableChild(obj.name, meshFileId, meshGuid, myTransformId)
			children += '\n' + self.CHILD_TRANSFORM_TEMPLATE.replace(REPLACE_INDICATOR, str(gameObjectIdAndTransformId[1]))
		elif len(obj.children) == 0:
			children = '[]'
		rotation = mathutils.Quaternion((0, 0, 0, 1))
		lines = dataText.split('\n')
		for line in lines:
			if line.startswith(obj.name):
				rotationComponents = line.split(', ')[1 :]
				rotation.x = float(rotationComponents[0])
				rotation.y = float(rotationComponents[1])
				rotation.z = float(rotationComponents[2])
				rotation.w = float(rotationComponents[3])
		# previousObjectRotationMode = obj.rotation_mode
		# obj.rotation_mode = 'XYZ'
		# rotation = obj.rotation_euler
		# if obj.type == 'CAMERA':
		# 	rotation.x += PI / 2
		# 	rotation.y += PI
		# 	rotation.z += PI
		# rotation = rotation.to_quaternion()
		# obj.rotation_mode = previousObjectRotationMode
		transform = self.TRANSFORM_TEMPLATE
		transform = transform.replace(REPLACE_INDICATOR + '10', str(obj.scale.z))
		transform = transform.replace(REPLACE_INDICATOR + '11', str(obj.scale.y))
		transform = transform.replace(REPLACE_INDICATOR + '12', children)
		transform = transform.replace(REPLACE_INDICATOR + '13', str(parentTransformId))
		transform = transform.replace(REPLACE_INDICATOR + '0', str(myTransformId))
		transform = transform.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
		transform = transform.replace(REPLACE_INDICATOR + '2', str(rotation.x))
		transform = transform.replace(REPLACE_INDICATOR + '3', str(rotation.y))
		transform = transform.replace(REPLACE_INDICATOR + '4', str(rotation.z))
		transform = transform.replace(REPLACE_INDICATOR + '5', str(rotation.w))
		transform = transform.replace(REPLACE_INDICATOR + '6', str(obj.location.x))
		transform = transform.replace(REPLACE_INDICATOR + '7', str(obj.location.z))
		transform = transform.replace(REPLACE_INDICATOR + '8', str(obj.location.y))
		transform = transform.replace(REPLACE_INDICATOR + '9', str(obj.scale.x))
		self.gameObjectsAndComponentsText += transform + '\n'
		self.transformIds.append(myTransformId)
		self.lastId += 1
		if obj.type == 'EMPTY' and obj.empty_display_type == 'IMAGE':
			spritePath = obj.data.filepath
			spritePath = os.path.expanduser('~') + spritePath[1 :]
			spriteName = spritePath[spritePath.rfind('/') + 1 :]
			newSpritePath = os.path.join(self.projectExportPath, 'Assets', 'Art', 'Textures', spriteName)
			spriteGuid = GetGuid(newSpritePath)
			spriteMeta = self.SPRITE_META_TEMPLATE
			spriteMeta = spriteMeta.replace(REPLACE_INDICATOR + '0', spriteGuid)
			spriteMeta = spriteMeta.replace(REPLACE_INDICATOR + '1', spriteName)
			open(newSpritePath + '.meta', 'wb').write(spriteMeta.encode('utf-8'))
			spriteRenderer = self.SPRITE_RENDERER_TEMPLATE
			spriteRenderer = spriteRenderer.replace(REPLACE_INDICATOR + '0', str(self.lastId))
			spriteRenderer = spriteRenderer.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
			spriteRenderer = spriteRenderer.replace(REPLACE_INDICATOR + '2', '0')
			spriteRenderer = spriteRenderer.replace(REPLACE_INDICATOR + '3', '0')
			spriteRenderer = spriteRenderer.replace(REPLACE_INDICATOR + '4', '0')
			spriteRenderer = spriteRenderer.replace(REPLACE_INDICATOR + '5', spriteGuid)
			self.gameObjectsAndComponentsText += spriteRenderer + '\n'
			self.componentIds.append(self.lastId)
			self.lastId += 1
		elif obj.type == 'LIGHT':
			lightObject = bpy.data.lights[obj.name]
			lightType = 2
			if lightObject.type == 'SUN':
				lightType = 1
			elif lightObject.type == 'SPOT':
				lightType = 0
			elif lightObject.type == 'AREA':
				lightType = 3
			spotSize = 0
			innerSpotAngle = 0
			if lightType == 0:
				spotSize = lightObject.spot_size
				innerSpotAngle = spotSize * (1.0 - lightObject.spot_blend)
			light = self.LIGHT_TEMPLATE
			light = light.replace(REPLACE_INDICATOR + '0', str(self.lastId))
			light = light.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
			light = light.replace(REPLACE_INDICATOR + '2', str(lightType))
			light = light.replace(REPLACE_INDICATOR + '3', str(lightObject.color[0]))
			light = light.replace(REPLACE_INDICATOR + '4', str(lightObject.color[1]))
			light = light.replace(REPLACE_INDICATOR + '5', str(lightObject.color[2]))
			light = light.replace(REPLACE_INDICATOR + '6', str(lightObject.energy * WATTS_TO_CANDELAS))
			light = light.replace(REPLACE_INDICATOR + '7', str(10))
			light = light.replace(REPLACE_INDICATOR + '8', str(spotSize))
			light = light.replace(REPLACE_INDICATOR + '9', str(innerSpotAngle))
			self.gameObjectsAndComponentsText += light + '\n'
			self.componentIds.append(self.lastId)
			self.lastId += 1
		elif obj.type == 'MESH':
			meshFilter = self.MESH_FILTER_TEMPLATE
			meshFilter = meshFilter.replace(REPLACE_INDICATOR + '0', str(self.lastId))
			meshFilter = meshFilter.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
			meshFilter = meshFilter.replace(REPLACE_INDICATOR + '2', meshFileId)
			meshFilter = meshFilter.replace(REPLACE_INDICATOR + '3', meshGuid)
			self.gameObjectsAndComponentsText += meshFilter + '\n'
			self.componentIds.append(self.lastId)
			self.lastId += 1
			for modifier in obj.modifiers:
				if modifier.type == 'COLLISION':
					self.AddMeshCollider (gameObjectId, False, False, meshFileId, meshGuid)
					break
			if obj.rigid_body != None:
				rigidbody = self.RIGIDBODY_TEMPLATE
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '0', str(self.lastId))
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '2', str(obj.rigid_body.mass))
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '3', str(obj.rigid_body.linear_damping))
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '4', str(obj.rigid_body.angular_damping))
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '5', '1')
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '6', str(int(obj.rigid_body.enabled)))
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '7', '0')
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '8', '0')
				rigidbody = rigidbody.replace(REPLACE_INDICATOR + '9', '0')
				self.gameObjectsAndComponentsText += rigidbody + '\n'
				self.componentIds.append(self.lastId)
				self.lastId += 1
			materials = ''
			for materialSlot in obj.material_slots:
				filePath = self.projectExportPath + '/Assets/Art/Materials/' + materialSlot.material.name + '.mat.meta'
				materialGuid = GetGuid(filePath)
				open(filePath, 'w').write('guid: ' + materialGuid)
				if self.unityVersionPath != '':
					dataText = open('/tmp/HolyBlender Data (BlenderToUnity)', 'rb').read().decode('utf-8')
					fileIdIndicator = '-' + self.projectExportPath + '/Assets/Art/Materials/' + materialSlot.material.name + '.mat'
					indexOfFile = dataText.find(fileIdIndicator)
					indexOfFileId = indexOfFile + len(fileIdIndicator) + 1
					indexOfEndOfFileId = dataText.find(' ', indexOfFileId)
					fileId = dataText[indexOfFileId : indexOfEndOfFileId]
				else:
					fileId = '10303'
				material = self.MATERIAL_TEMPLATE
				material = material.replace(REPLACE_INDICATOR + '0', fileId)
				material = material.replace(REPLACE_INDICATOR + '1', materialGuid)
				materials += material + '\n'
			materials = materials[: -1]
			meshRenderer = self.MESH_RENDERER_TEMPLATE
			meshRenderer = meshRenderer.replace(REPLACE_INDICATOR + '0', str(self.lastId))
			meshRenderer = meshRenderer.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
			meshRenderer = meshRenderer.replace(REPLACE_INDICATOR + '2', materials)
			self.gameObjectsAndComponentsText += meshRenderer + '\n'
			self.componentIds.append(self.lastId)
			self.lastId += 1
		elif obj.type == 'CAMERA':
			cameraObject = bpy.data.cameras[obj.name]
			fovAxisMode = 0
			if cameraObject.sensor_fit == 'HORIZONTAL':
				fovAxisMode = 1
			isOrthographic = 0
			if cameraObject.type == 'ORTHO':
				isOrthographic = 1
			camera = self.CAMERA_TEMPLATE
			camera = camera.replace(REPLACE_INDICATOR + '0', str(self.lastId))
			camera = camera.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
			camera = camera.replace(REPLACE_INDICATOR + '2', str(fovAxisMode))
			camera = camera.replace(REPLACE_INDICATOR + '3', str(cameraObject.clip_start))
			camera = camera.replace(REPLACE_INDICATOR + '4', str(cameraObject.clip_end))
			camera = camera.replace(REPLACE_INDICATOR + '5', str(cameraObject.angle * (180.0 / PI)))
			camera = camera.replace(REPLACE_INDICATOR + '6', str(isOrthographic))
			camera = camera.replace(REPLACE_INDICATOR + '7', str(cameraObject.ortho_scale / 2))
			self.gameObjectsAndComponentsText += camera + '\n'
			self.componentIds.append(self.lastId)
			self.lastId += 1
		attachedScripts = attachedUnityScriptsDict.get(obj, [])
		for scriptName in attachedScripts:
			filePath = self.projectExportPath + '/Assets/Scripts/' + scriptName
			MakeFolderForFile (filePath)
			for textBlock in bpy.data.texts:
				if textBlock.name == scriptName:
					if not scriptName.endswith('.cs'):
						filePath += '.cs'
					scriptText = textBlock.as_string()
					open(filePath, 'wb').write(scriptText.encode('utf-8'))
					break
			filePath += '.meta'
			scriptGuid = GetGuid(filePath)
			open(filePath, 'w').write('guid: ' + scriptGuid)
			script = self.SCRIPT_TEMPLATE
			script = script.replace(REPLACE_INDICATOR + '0', str(self.lastId))
			script = script.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
			script = script.replace(REPLACE_INDICATOR + '2', scriptGuid)
			self.gameObjectsAndComponentsText += script + '\n'
			self.componentIds.append(self.lastId)
			self.lastId += 1
		indexOfComponentsList = self.gameObjectsAndComponentsText.find(REPLACE_INDICATOR + '2')
		for componentId in self.componentIds:
			component = self.COMPONENT_TEMPLATE
			component = component.replace(REPLACE_INDICATOR, str(componentId))
			self.gameObjectsAndComponentsText = self.gameObjectsAndComponentsText[: indexOfComponentsList] + component + '\n' + self.gameObjectsAndComponentsText[indexOfComponentsList :]
		self.gameObjectsAndComponentsText = self.gameObjectsAndComponentsText.replace(REPLACE_INDICATOR + '2', '')
		return myTransformId

	def AddMeshCollider (self, gameObjectId : int, isTirgger : bool, isConvex : bool, fileId : str, meshGuid : str):
		meshCollider = self.MESH_COLLIDER_TEMPLATE
		meshCollider = meshCollider.replace(REPLACE_INDICATOR + '0', str(self.lastId))
		meshCollider = meshCollider.replace(REPLACE_INDICATOR + '1', str(gameObjectId))
		meshCollider = meshCollider.replace(REPLACE_INDICATOR + '2', str(int(isTirgger)))
		meshCollider = meshCollider.replace(REPLACE_INDICATOR + '3', str(int(isConvex)))
		meshCollider = meshCollider.replace(REPLACE_INDICATOR + '4', fileId)
		meshCollider = meshCollider.replace(REPLACE_INDICATOR + '5', meshGuid)
		self.gameObjectsAndComponentsText += meshCollider + '\n'
		self.componentIds.append(self.lastId)
		self.lastId += 1

	def MakeClickableChild (self, name : str, fileId : str, meshGuid : str, parentTransformId = 0) -> (int, int):
		gameObjectIdAndTransformId = self.MakeEmptyObject(name, 31, parentTransformId)
		self.AddMeshCollider (gameObjectIdAndTransformId[0], True, True, fileId, meshGuid)
		return gameObjectIdAndTransformId

class UnrealTranslateButton (bpy.types.Operator):
	bl_idname = 'unreal.translate'
	bl_label = 'Translate To Unreal'

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		global operatorContext
		global currentTextBlock
		BuildTool ('UnityToUnreal')
		operatorContext = context
		MakeFolderForFile ('/tmp/HolyBlender (Unreal Scripts)/')
		script = currentTextBlock.name
		if not currentTextBlock.name.endswith('.cs'):
			script += '.cs'
		filePath = '/tmp/HolyBlender (Unreal Scripts)/' + script
		open(filePath, 'wb').write(currentTextBlock.as_string().encode('utf-8'))
		ConvertCSFileToCPP (filePath)

class BevyTranslateButton (bpy.types.Operator):
	bl_idname = 'bevy.translate'
	bl_label = 'Translate To Bevy'

	@classmethod
	def poll (cls, context):
		return True
	
	def execute (self, context):
		global operatorContext
		global currentTextBlock
		BuildTool ('UnityToBevy')
		operatorContext = context
		script = currentTextBlock.name
		if not currentTextBlock.name.endswith('.cs'):
			script += '.cs'
		filePath = '/tmp/' + script
		open(filePath, 'wb').write(currentTextBlock.as_string().encode('utf-8'))
		ConvertCSFileToRust (filePath)

timer = None
class Loop (bpy.types.Operator):
	bl_idname = 'blender_plugin.start'
	bl_label = 'blender_plugin_start'
	bl_options = { 'REGISTER' }

	def modal (self, context, event):
		for area in bpy.data.screens['Layout'].areas:
			if area.type == 'VIEW_3D':
				for region in area.regions:
					if region.type == 'WINDOW':
						region.tag_redraw()
		return {'PASS_THROUGH'} # Won't supress event bubbles

	def invoke (self, context, event):
		global timer
		if timer is None:
			timer = self._timer = context.window_manager.event_timer_add(
				time_step=0.016666667,
				window=context.window)
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		return {'FINISHED'}

	def execute (self, context):
		return self.invoke(context, None)

classes = [
	UnrealExportButton,
	BevyExportButton,
	UnityExportButton,
	GodotExportButton,
	HTMLExportButton,
	PlayButton,
	UnrealTranslateButton,
	BevyTranslateButton,
	ExamplesOperator,
	ExamplesMenu,
	AttachedObjectsMenu,
	Loop,
	UnityScriptsPanel,
	UnrealScriptsPanel,
	GodotScriptsPanel,
	BevyScriptsPanel,
	WorldPanel
]

def BuildTool (toolName : str):
	command = [ 'make', 'build_' + toolName ]
	print(command)

	subprocess.check_call(command)

def ExportMesh (obj, folder : str) -> str:
	filePath = os.path.join(folder, obj.name + '.fbx')
	filePath = filePath.replace(' ', '_')
	bpy.ops.object.select_all(action='DESELECT')
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
	bpy.ops.export_scene.fbx(filepath=filePath, use_selection=True, use_custom_props=True, mesh_smooth_type='FACE')
	return filePath

def GetObjectBounds (obj) -> (mathutils.Vector, mathutils.Vector):
	_min = mathutils.Vector((float('inf'), float('inf'), float('inf')))
	_max = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))
	if obj.type == 'MESH':
		for vertex in obj.data.vertices:
			_min.x = min((obj.matrix_world @ vertex.co).x, _min.x)
			_min.y = min((obj.matrix_world @ vertex.co).y, _min.y)
			_min.z = min((obj.matrix_world @ vertex.co).z, _min.z)
			_max.x = max((obj.matrix_world @ vertex.co).x, _max.x)
			_max.y = max((obj.matrix_world @ vertex.co).y, _max.y)
			_max.z = max((obj.matrix_world @ vertex.co).z, _max.z)
	else:
		print('GetObjectBounds is not implemented for object types besides meshes')
	return ((_min + _max) / 2, _max - _min)

def GetGuid (filePath : str):
	return hashlib.md5(filePath.encode('utf-8')).hexdigest()

def ConvertCSFileToCPP (filePath):
	global mainClassNames
	global unrealCodePath
	global unrealCodePathSuffix
	assert os.path.isfile(filePath)
	unrealCodePath = os.path.expanduser(operatorContext.scene.world.unrealExportPath)
	unrealProjectName = unrealCodePath[unrealCodePath.rfind('/') + 1 :]
	unrealCodePathSuffix = '/Source/' + unrealProjectName
	unrealCodePath += unrealCodePathSuffix
	mainClassNames = [ os.path.split(filePath)[-1].split('.')[0] ]
	command = [
		'dotnet',
		os.path.expanduser('~/HolyBlender/UnityToUnreal/HolyBlender.dll'),
		'includeFile=' + filePath,
		'unreal=true',
		'output=' + unrealCodePath,
	]
	# for arg in sys.argv:
	# 	command.append(arg)
	command.append(os.path.expanduser(operatorContext.scene.world.unity_project_import_path))
	print(command)

	subprocess.check_call(command)

	outputFilePath = unrealCodePath + filePath[filePath.rfind('/') :]
	outputFilePath = outputFilePath.replace('.cs', '.py')
	print(outputFilePath)
	assert os.path.isfile(outputFilePath)

	os.system('cat ' + outputFilePath)

	ConvertPythonFileToCPP (outputFilePath)

def ConvertPythonFileToCPP (filePath):
	global mainClassNames
	lines = []
	for line in open(filePath, 'rb').read().decode('utf-8').splitlines():
		if line.startswith('import ') or line.startswith('from '):
			print('Skipping line:', line)
			continue
		lines.append(line)
	text = '\n'.join(lines)
	open(filePath, 'wb').write(text.encode('utf-8'))
	hasCorrectTextBlock = False
	textBlockName = filePath[filePath.rfind('/') + 1 :]
	for textBlock in bpy.data.texts:
		if textBlock.name == textBlockName:
			hasCorrectTextBlock = True
			break
	if not hasCorrectTextBlock:
		bpy.data.texts.new(textBlockName)
	textBlock = bpy.data.texts[textBlockName]
	textBlock.clear()
	textBlock.write(text)
	outputFilePath = unrealCodePath + '/' + textBlockName
	command = [ 'python3', os.path.expanduser('~/HolyBlender') + '/py2many/py2many.py', '--cpp=1', outputFilePath, '--unreal=1', '--outdir=' + unrealCodePath ]
	# for arg in sys.argv:
	# 	command.append(arg)
	command.append(os.path.expanduser(operatorContext.scene.world.unrealExportPath))
	print(command)
	
	subprocess.check_call(command)

	outputFileText = open(outputFilePath.replace('.py', '.cpp'), 'rb').read().decode('utf-8')
	for mainClassName in mainClassNames:
		indexOfMainClassName = 0
		while indexOfMainClassName != -1:
			indexOfMainClassName = outputFileText.find(mainClassName, indexOfMainClassName + len(mainClassName))
			if indexOfMainClassName != -1 and outputFileText[indexOfMainClassName - 1 : indexOfMainClassName] != 'A' and not IsInString_CS(outputFileText, indexOfMainClassName):
				outputFileText = outputFileText[: indexOfMainClassName] + 'A' + outputFileText[indexOfMainClassName :]
		equalsNullIndicator = '= nullptr'
		indexOfEqualsNull = 0
		while indexOfEqualsNull != -1:
			indexOfEqualsNull = outputFileText.find(equalsNullIndicator, indexOfEqualsNull + len(equalsNullIndicator))
			if indexOfEqualsNull != -1:
				indexOfSpace = outputFileText.rfind(' ', 0, indexOfEqualsNull - 1)
				indexOfMainClassName = outputFileText.rfind(mainClassName, 0, indexOfSpace)
				if indexOfMainClassName == indexOfSpace - len(mainClassName):
					outputFileText = Remove(outputFileText, indexOfEqualsNull, len(equalsNullIndicator))
	pythonFileText = open(outputFilePath, 'rb').read().decode('utf-8')
	pythonFileLines = pythonFileText.split('\n')
	headerFileText = open(outputFilePath.replace('.py', '.h'), 'rb').read().decode('utf-8')
	for i in range(len(pythonFileLines) - 1, -1, -1):
		line = pythonFileLines[i]
		if not line.startswith(' '):
			line = line.replace(' ', '')
			indexOfColon = line.find(':')
			variableName = line[: indexOfColon]
			mainClassName = os.path.split(outputFilePath)[-1].split('.')[0]
			outputFileText = outputFileText.replace(variableName, variableName + '_' + mainClassName)
			headerFileText = headerFileText.replace(variableName, variableName + '_' + mainClassName)
			indexOfVariableName = headerFileText.find(variableName)
			indexOfNewLine = headerFileText.rfind('\n', 0, indexOfVariableName)
			headerFileText = headerFileText[: indexOfNewLine] + '\n\tUPROPERTY(EditAnywhere)' + headerFileText[indexOfNewLine :]
			indexOfEquals = line.find('=', indexOfColon + 1)
			variableName += '_' + mainClassName
			mainConstructor = '::A' + mainClassName + '() {'
			indexOfMainConstructor = outputFileText.find(mainConstructor)
			if indexOfEquals != -1:
				value = line[indexOfEquals + 1 :]
				outputFileText = outputFileText[: indexOfMainConstructor + len(mainConstructor) + 1] + '\t' + variableName + ' = ' + value + ';\n' + outputFileText[indexOfMainConstructor + len(mainConstructor) + 1 :]
		else:
			break
	outputFileLines = outputFileText.split('\n')
	for i in range(len(outputFileLines)):
		line = outputFileLines[i]
		line = line.replace(' ', '')
		indexOfX = 0
		while indexOfX != -1:
			indexOfX = line.find('.X', indexOfX + 1)
			if indexOfX != -1:
				indexOfEquals = line.find('=', indexOfX)
				if indexOfEquals != -1 and indexOfEquals <= indexOfX + 3:
					outputFileLines[i] = line[: indexOfEquals + 1] + '-' + line[indexOfEquals + 1 :]
	outputFileText = '\n'.join(outputFileLines)
	cppFilePath = outputFilePath.replace('.py', '.cpp')
	open(cppFilePath, 'wb').write(outputFileText.encode('utf-8'))
	open(outputFilePath.replace('.py', '.h'), 'wb').write(headerFileText.encode('utf-8'))
	command = [ 'cat', cppFilePath ]
	print(command)

	subprocess.check_call(command)
	
	for textBlock in bpy.data.texts:
		textBlockName = cppFilePath[cppFilePath.rfind('/') + 1 :].replace('.cpp', '')
		if textBlock.name == textBlockName:
			textBlockName += '.cpp+.h'
			hasCorrectTextBlock = False
			for textBlock in bpy.data.texts:
				if textBlock.name == textBlockName:
					hasCorrectTextBlock = True
					break
			if not hasCorrectTextBlock:
				bpy.data.texts.new(textBlockName)
			textBlock = bpy.data.texts[textBlockName]
			textBlock.clear()
			textBlock.write(outputFileText)
			textBlock.write(headerFileText)

def ConvertCSFileToRust (filePath):
	global mainClassName
	mainClassName = filePath[filePath.rfind('/') + 1 : filePath.rfind('.')]
	assert os.path.isfile(filePath)
	MakeFolderForFile ('/tmp/src/main.rs')
	MakeFolderForFile ('/tmp/assets/registry.json')
	data = 'output=/tmp\n' + filePath
	open('/tmp/HolyBlender Data (UnityToBevy)', 'wb').write(data.encode('utf-8'))
	command = [
		'dotnet',
		os.path.expanduser('~/HolyBlender/UnityToBevy/HolyBlender.dll'), 
		'includeFile=' + filePath,
		'bevy=true',
		'output=/tmp'
	]
	# for arg in sys.argv:
	# 	command.append(arg)
	print(command)

	subprocess.check_call(command)

	outputFilePath = '/tmp/main.py'
	print(outputFilePath)
	assert os.path.isfile(outputFilePath)

	os.system('cat ' + outputFilePath)

	ConvertPythonFileToRust (outputFilePath)

def ConvertPythonFileToRust (filePath):
	global mainClassName
	lines = []
	for line in open(filePath, 'rb').read().decode('utf-8').splitlines():
		if line.startswith('import ') or line.startswith('from '):
			print('Skipping line:', line)
			continue
		lines.append(line)
	text = '\n'.join(lines)
	open(filePath, 'wb').write(text.encode('utf-8'))
	hasCorrectTextBlock = False
	textBlockName = filePath[filePath.rfind('/') + 1 :]
	for textBlock in bpy.data.texts:
		if textBlock.name == textBlockName:
			hasCorrectTextBlock = True
			break
	if not hasCorrectTextBlock:
		bpy.data.texts.new(textBlockName)
	textBlock = bpy.data.texts[textBlockName]
	textBlock.clear()
	textBlock.write(text)
	command = [ 'python3', 'py2many/py2many.py', '--rust=1', '--force', filePath, '--outdir=/tmp/src' ]
	# for arg in sys.argv:
	# 	command.append(arg)
	command.append(os.path.expanduser(operatorContext.scene.world.unity_project_import_path))
	print(command)
	
	subprocess.check_call(command)

	outputFilePath = '/tmp/src/main.rs'
	assert os.path.isfile(outputFilePath)
	print(outputFilePath)

	os.system('cat ' + outputFilePath)
	
	data = open('/tmp/HolyBlender Data (UnityToBevy)', 'rb').read().decode('utf-8')
	filePath = data[data.find('\n') + 1 :]
	for textBlock in bpy.data.texts:
		if textBlock.name == filePath[filePath.rfind('/') + 1 :].replace('.rs', '.cs'):
			textBlock.name = textBlock.name.replace('.cs', '.rs')
			textBlock.clear()
			outputFileText = open('/tmp/src/main.rs', 'rb').read().decode('utf-8')
			textBlock.write(outputFileText)

def DrawExamplesMenu (self, context):
	self.layout.menu(ExamplesMenu.bl_idname)

def DrawAttachedObjectsMenu (self, context):
	self.layout.menu(AttachedObjectsMenu.bl_idname)

def DrawUnrealTranslateButton (self, context):
	self.layout.operator(UnrealTranslateButton.bl_idname, icon='CONSOLE')

def DrawBevyTranslateButton (self, context):
	self.layout.operator(BevyTranslateButton.bl_idname, icon='CONSOLE')

def SetupTextEditorFooterContext (self, context):
	global currentTextBlock
	global previousRunningScripts
	currentTextBlock = context.edit_text
	previousRunningScripts = []
	for textBlock in bpy.data.texts:
		if textBlock.run_cs and textBlock.name != '.gltf_auto_export_gltf_settings':
			previousRunningScripts.append(textBlock.name)

def DrawRunCSToggle (self, context):
	self.layout.prop(context.edit_text, 'run_cs')

def DrawIsInitScriptToggle (self, context):
	self.layout.prop(context.edit_text, 'is_init_script')

def OnUpdateUnityScripts (self, context):
	global attachedUnityScriptsDict
	attachedScripts = []
	for i in range(MAX_SCRIPTS_PER_OBJECT):
		script = getattr(self, 'unity_script' + str(i))
		if script != None:
			attachedScripts.append(script.name)
	attachedUnityScriptsDict[self] = attachedScripts

def OnUpdateUnrealScripts (self, context):
	global attachedUnrealScriptsDict
	attachedScripts = []
	for i in range(MAX_SCRIPTS_PER_OBJECT):
		script = getattr(self, 'unreal_script' + str(i))
		if script != None:
			attachedScripts.append(script.name)
	attachedUnrealScriptsDict[self] = attachedScripts

def OnUpdateGodotScripts (self, context):
	global attachedGodotScriptsDict
	attachedScripts = []
	for i in range(MAX_SCRIPTS_PER_OBJECT):
		script = getattr(self, 'godotScript' + str(i))
		if script != None:
			attachedScripts.append(script.name)
	attachedGodotScriptsDict[self] = attachedScripts

def OnUpdateBevyScripts (self, context):
	global attachedBevyScriptsDict
	attachedScripts = []
	for i in range(MAX_SCRIPTS_PER_OBJECT):
		script = getattr(self, 'bevy_script' + str(i))
		if script != None:
			attachedScripts.append(script.name)
	attachedBevyScriptsDict[self] = attachedScripts

def UpdateInspectorFields (textBlock):
	global attachedUnityScriptsDict
	global propertiesTypesDict
	global propertiesDefaultValuesDict
	text = textBlock.as_string()
	publicIndicator = 'public '
	indexOfPublicIndicator = text.find(publicIndicator)
	while indexOfPublicIndicator != -1:
		indexOfType = indexOfPublicIndicator + len(publicIndicator)
		if text[indexOfType :].startswith('class '):
			indexOfPublicIndicator = text.find(publicIndicator, indexOfType)
			continue
		indexOfVariableName = indexOfType
		while indexOfVariableName < len(text) - 1:
			indexOfVariableName += 1
			if text[indexOfVariableName] != ' ':
				break
		if text[indexOfVariableName + 1] == '(':
			indexOfPublicIndicator = text.find(publicIndicator, indexOfType)
			continue
		indexOfVariableName = text.find(' ', indexOfVariableName + 1)
		type = text[indexOfType : indexOfVariableName]
		indexOfPotentialEndOfVariable = IndexOfAny(text, [ ' ', ';' , '=' ], indexOfVariableName + 1)
		variableName = text[indexOfVariableName : indexOfPotentialEndOfVariable]
		variableName = variableName.strip()
		shouldBreak = False
		for obj in attachedUnityScriptsDict.keys():
			for attachedScript in attachedUnityScriptsDict[obj]:
				if attachedScript == textBlock.name:
					value = ''
					isSetToValue = False
					if text[indexOfPotentialEndOfVariable] == '=':
						indexOfSemicolon = text.find(';', indexOfPotentialEndOfVariable + 1)
						value = text[indexOfPotentialEndOfVariable + 1 : indexOfSemicolon]
						value = value.strip()
						isSetToValue = True
					if type == 'int':
						if not isSetToValue:
							value = 0
						else:
							value = int(value)
					elif type == 'float' or type == 'double':
						if not isSetToValue:
							value = 0.0
						else:
							value = value.replace('f', '')
							value = float(value)
					elif type == 'bool':
						if not isSetToValue:
							value = False
						elif value == 'true':
							value = True
						else:
							value = False
					attachedScript = attachedScript.replace('.cs', '')
					attachedScript = attachedScript.replace('.cpp', '')
					attachedScript = attachedScript.replace('.h', '')
					propertyName = variableName + '_' + attachedScript
					if propertyName not in obj.keys():
						obj[propertyName] = value
						propertiesDefaultValuesDict[variableName] = value
					else:
						propertiesDefaultValuesDict[variableName] = obj[propertyName]
					propertiesTypesDict[variableName] = type
					shouldBreak = True
					break
			if shouldBreak:
				break
		indexOfPublicIndicator = text.find(publicIndicator, indexOfType)

def OnRedrawView ():
	global currentTextBlock
	global textBlocksTextsDict
	global attachedUnityScriptsDict
	global previousRunningScripts
	global previousTextBlocksTextsDict
	textBlocksTextsDict = {}
	for textBlock in bpy.data.texts:
		if textBlock.name == '.gltf_auto_export_gltf_settings':
			continue
		textBlocksTextsDict[textBlock.name] = textBlock.as_string()
		if textBlock.name not in previousTextBlocksTextsDict or previousTextBlocksTextsDict[textBlock.name] != textBlock.as_string():
			UpdateInspectorFields (textBlock)
	previousTextBlocksTextsDict = textBlocksTextsDict.copy()
	bpy.types.TEXT_HT_footer.remove(SetupTextEditorFooterContext)
	bpy.types.TEXT_HT_footer.append(SetupTextEditorFooterContext)
	if currentTextBlock != None:
		if currentTextBlock.run_cs:
			import RunCSInBlender as runCSInBlender
			for obj in attachedUnityScriptsDict:
				if currentTextBlock.name in attachedUnityScriptsDict[obj]:
					filePath = os.path.expanduser('/tmp/HolyBlender Data (UnityInBlender)/' + currentTextBlock.name)
					filePath = filePath.replace('.cs', '.py')
					if not filePath.endswith('.py'):
						filePath += '.py'
					if currentTextBlock.name not in previousRunningScripts:
						MakeFolderForFile (filePath)
						open(filePath, 'wb').write(currentTextBlock.as_string().encode('utf-8'))
						BuildTool ('UnityInBlender')
						command = [
							'dotnet',
							os.path.expanduser('~/HolyBlender/UnityInBlender/HolyBlender.dll'), 
							'includeFile=' + filePath,
							'output=/tmp/HolyBlender Data (UnityInBlender)'
						]
						print(command)

						subprocess.check_call(command)
					runCSInBlender.Run (filePath, obj)
	# id = 0
	# size = 32
	# blf.size(id, size)
	# blf.color(id, 0, 1, 0, 0.8)
	# x = 0
	# y = 0
	# blf.draw(id, 'Hello World!')

def register ():
	MakeFolderForFile ('/tmp/')
	registryText = open(TEMPLATE_REGISTRY_PATH, 'rb').read().decode('utf-8')
	registryText = registryText.replace('ꗈ', '')
	open(REGISTRY_PATH, 'wb').write(registryText.encode('utf-8'))
	registry = bpy.context.window_manager.components_registry
	registry.schemaPath = REGISTRY_PATH
	bpy.ops.object.reload_registry()
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.World.unity_project_import_path = bpy.props.StringProperty(
		name = 'Unity project import path',
		description = '',
		default = ''
	)
	bpy.types.World.unity_project_export_path = bpy.props.StringProperty(
		name = 'Unity project export path',
		description = '',
		default = '~/TestUnityProject'
	)
	# bpy.types.World.unity_export_version = bpy.props.StringProperty(
	# 	name = 'Unity export version',
	# 	description = '',
	# 	default = ''
	# )
	bpy.types.World.unrealExportPath = bpy.props.StringProperty(
		name = 'Unreal project path',
		description = '',
		default = '~/TestUnrealProject'
	)
	bpy.types.World.godotExportPath = bpy.props.StringProperty(
		name = 'Godot project path',
		description = '',
		default = '~/TestGodotProject'
	)
	bpy.types.World.bevy_project_path = bpy.props.StringProperty(
		name = 'Bevy project path',
		description = '',
		default = '~/TestBevyProject'
	)
	bpy.types.World.htmlExportPath = bpy.props.StringProperty(
		name = 'HTML project path',
		description = '',
		default = '~/TestHtmlProject'
	)
	bpy.types.World.holyserver = bpy.props.PointerProperty(name='Python Server', type=bpy.types.Text)
	bpy.types.World.html_code = bpy.props.PointerProperty(name='HTML code', type=bpy.types.Text)
	bpy.types.Object.html_on_click = bpy.props.PointerProperty(name='JavaScript on click', type=bpy.types.Text)
	bpy.types.Object.html_css = bpy.props.PointerProperty(name='CSS', type=bpy.types.Text)
	bpy.types.Text.run_cs = bpy.props.BoolProperty(
		name = 'Run C# Script',
		description = ''
	)
	bpy.types.Text.is_init_script = bpy.props.BoolProperty(
		name = 'Is Initialization Script',
		description = ''
	)
	bpy.types.TEXT_HT_header.append(DrawExamplesMenu)
	bpy.types.TEXT_HT_header.append(DrawAttachedObjectsMenu)
	bpy.types.TEXT_HT_footer.append(DrawUnrealTranslateButton)
	bpy.types.TEXT_HT_footer.append(DrawBevyTranslateButton)
	bpy.types.TEXT_HT_footer.append(DrawRunCSToggle)
	bpy.types.TEXT_HT_footer.append(DrawIsInitScriptToggle)
	for i in range(MAX_SCRIPTS_PER_OBJECT):
		setattr(bpy.types.Object, 'unity_script' + str(i), bpy.props.PointerProperty(name='Attach Unity script', type=bpy.types.Text, update=OnUpdateUnityScripts))
		setattr(bpy.types.Object, 'unreal_script' + str(i), bpy.props.PointerProperty(name='Attach Unreal script', type=bpy.types.Text, update=OnUpdateUnrealScripts))
		setattr(bpy.types.Object, 'godotScript' + str(i), bpy.props.PointerProperty(name='Attach Godot script', type=bpy.types.Text, update=OnUpdateGodotScripts))
		setattr(bpy.types.Object, 'bevy_script' + str(i), bpy.props.PointerProperty(name='Attach bevy script', type=bpy.types.Text, update=OnUpdateBevyScripts))
	for obj in bpy.data.objects:
		attachedScripts = []
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			script = getattr(obj, 'unity_script' + str(i))
			if script != None:
				attachedScripts.append(script.name)
		attachedUnityScriptsDict[obj] = attachedScripts
		attachedScripts = []
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			script = getattr(obj, 'unreal_script' + str(i))
			if script != None:
				attachedScripts.append(script.name)
		attachedUnrealScriptsDict[obj] = attachedScripts
		attachedScripts = []
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			script = getattr(obj, 'godotScript' + str(i))
			if script != None:
				attachedScripts.append(script.name)
		attachedGodotScriptsDict[obj] = attachedScripts
		attachedScripts = []
		for i in range(MAX_SCRIPTS_PER_OBJECT):
			script = getattr(obj, 'bevy_script' + str(i))
			if script != None:
				attachedScripts.append(script.name)
		attachedBevyScriptsDict[obj] = attachedScripts
	handle = bpy.types.SpaceView3D.draw_handler_add(
		OnRedrawView,
		tuple([]),
		'WINDOW', 'POST_PIXEL')
	bpy.ops.blender_plugin.start()

def unregister ():
	bpy.types.TEXT_HT_header.remove(DrawExamplesMenu)
	bpy.types.TEXT_HT_header.append(DrawAttachedObjectsMenu)
	bpy.types.TEXT_HT_footer.remove(DrawUnrealTranslateButton)
	bpy.types.TEXT_HT_footer.remove(DrawBevyTranslateButton)
	bpy.types.TEXT_HT_footer.remove(DrawRunCSToggle)
	bpy.types.TEXT_HT_footer.remove(DrawIsInitScriptToggle)
	for cls in classes:
		bpy.utils.unregister_class(cls)

def InitTexts ():
	if '__Html__.html' not in bpy.data.texts:
		textBlock = bpy.data.texts.new(name='__Html__.html')
		textBlock.from_string(INIT_HTML)
		if bpy.data.worlds[0].html_code == None:
			bpy.data.worlds[0].html_code = textBlock
	if '__Server__.py' not in bpy.data.texts:
		textBlock = bpy.data.texts.new(name='__Server__.py')
		textBlock.from_string(BLENDER_SERVER)
		if bpy.data.worlds[0].holyserver == None:
			bpy.data.worlds[0].holyserver = textBlock

if __name__ == '__main__':
	register ()
	InitTexts ()
	if user_args:
		for arg in user_args:
			if arg.endswith('.py'):
				print('exec:', arg)
				exec(open(arg).read())
			elif arg == '--test-unity':
				bpy.ops.unity.export()
