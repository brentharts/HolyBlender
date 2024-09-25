import subprocess, sys, os, install_UnityExport
os.system('rm /tmp/HolyBlender*')
monogame = netghost = False

TEST_BEVY = '''
txt = bpy.data.texts.new(name='rotate.rs')
txt.from_string('trs.rotate_y(5.0 * time.delta_seconds());)')
bpy.data.objects["Cube"].bevy_script0 = txt
bpy.ops.bevy.export()
'''

TEST_UNITY = '''
PI = 3.141592653589793

bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['Cube'].select_set(True)
bpy.ops.object.delete()
camera = bpy.data.objects['Camera']
camera.location = mathutils.Vector((0, 4, 0))
camera.rotation_mode = 'XYZ'
camera.rotation_euler = mathutils.Euler((PI / 2, 0, PI))
bpy.ops.mesh.primitive_monkey_add()
txtBlock = bpy.data.texts.new(name='Rotate')
txtBlock.from_string(EXAMPLES_DICT['Rotate (Unity)'])
setattr(bpy.data.objects['Suzanne'], 'unity_script0', txtBlock)
bpy.ops.object.select_all(action='DESELECT')
mat = bpy.data.materials.get("Material")
if mat is None:
	mat = bpy.data.materials.new(name="Material")
monkey = bpy.data.objects['Suzanne']
monkey.select_set(True)
monkey.data.materials.append(mat)
bpy.ops.unity.export()
'''

TEST_HTML = '''
from random import random

bpy.data.worlds[0].holyserver = bpy.data.texts['__Server__.py']

JS = """
window.alert(self);
var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
	console.log(this.readyState);
	console.log(this.status);
	console.log(self);
	if (this.readyState == 4 && this.status == 200) {
		self.innerHTML = xhttp.responseText.replaceAll('<', '[').replaceAll('>', ']');
	}
};
xhttp.overrideMimeType('text/plain; charset=utf-8');
xhttp.open('GET', self.getAttribute('id'), true);
xhttp.send();
"""

onclick = bpy.data.texts.new(name='onclick.js')
onclick.from_string(JS)

CSS = """
box-shadow: 5px 5px 10px black;
"""
css = bpy.data.texts.new(name='css')
css.from_string(CSS)

for i in range(0):
	bpy.ops.mesh.primitive_cube_add()
	ob = bpy.context.active_object
	ob.location.x = i * 3
	ob.location.z = -i * 3
	ob.rotation_euler = [random(), random(), random()]
	ob.html_on_click = onclick
	ob.html_css = css
bpy.ops.bevy.export()'''

blender = 'blender'
if sys.platform == 'win32': # Windows
	blender = 'C:/Program Files/Blender Foundation/Blender 4.2/blender.exe'
elif sys.platform == 'darwin': # Apple
	blender = '/Applications/Blender.app/Contents/MacOS/Blender'
command = []
user_script = None
user_opts = []
test_bevy = False
for i,arg in enumerate(sys.argv):
	if arg.endswith('.blend'):
		command.append(os.path.expanduser(arg))
	elif arg.endswith('.exe'): # Windows
		blender = arg
	elif arg.endswith('.app'): # Apple
		blender = arg + '/Contents/MacOS/Blender'
	elif arg.endswith(('blender', 'Blender')):
		blender = arg
	elif arg == '--eval':
		user_script = sys.argv[i + 1]
	elif arg == '--test-bevy':
		test_bevy = True
		tmp = '/tmp/__test_bevy__.py'
		open(tmp, 'w').write(TEST_BEVY)
		user_script = tmp
	elif arg == '--test-html':
		user_script = '/tmp/__test_html__.py'
		open(user_script, 'w').write(TEST_HTML)
	elif arg == '--test-unity':
		user_script = '/tmp/__test_unity__.py'
		open(user_script, 'w').write(TEST_UNITY)
	elif arg == '--ghost':
		netghost = True
	elif arg == '--monogame' in sys.argv:
		monogame = True
	elif arg.startswith('--'):
		user_opts.append(arg)

command = [blender] + command + [ '--python', 'MakeBlenderPlugin.py' ]

if user_script or user_opts:
	command.append('--')
if user_script:
	command.append(user_script)
if user_opts:
	command += user_opts
print(command)

if not os.path.isdir('./Blender_bevy_components_workflow'):
	cmd = 'git clone https://github.com/OpenSourceJesus/Blender_bevy_components_workflow --depth=1'
	print(cmd)
	
	subprocess.check_call(cmd.split())

if netghost and not os.path.isdir('./Net-Ghost-SE'):
	cmd = 'git clone https://github.com/brentharts/Net-Ghost-SE.git --depth=1'
	print(cmd)
	subprocess.check_call(cmd.split())

if monogame:
	if not os.path.isdir('./MonoGame'):
		cmd = 'git clone https://github.com/MonoGame/MonoGame.git --depth=1'
		print(cmd)
		subprocess.check_call(cmd.split())
	subprocess.check_call(['bash', './build.sh'], cwd='./MonoGame')

subprocess.check_call(command) # Run blender