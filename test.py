import os as os

from maya import mel as mel
from maya import cmds as cmds

mel.eval('source createAndAssignShader; ')

print 'Make sure you check the project and sub paths.'

print 'Starting script...'

DEBUG = False
ZB_SUFFIX = 'ZBrush_defualt_group'
SHADER_TYPES = ('diffuse', 'standard_bump')

if DEBUG:
    project_path = '/Users/destrado/Cache/MEL/'
    shot_name = 'shot01'
    sub_path = '{0}/'.format(shot_name)
else:
    project_path = 'E:/proj/thesis/'
    shot_name = 'shot99'
    sub_path = '02_shots/{0}/3d/zbrush/'.format(shot_name)


def runFileOperations(group_name):

    print """
--------------
Updating group {0}:{1}
--------------
""".format(group_name, ZB_SUFFIX)

    mel.eval('select -r {0}:{1};'.format(group_name, ZB_SUFFIX))

    print """
-- Assigning and connecting mia shaders...
"""

    node_name = mel.eval("""
    mrCreateCustomNode -asShader "assignCreatedShader %type \\"\\" %node \\"{0}:{1}\\";" mia_material_x_passes;
    """.format(group_name, ZB_SUFFIX))

    for i, type in enumerate(SHADER_TYPES):

        print """
-- Creating shader file and texture for node {0} and type {1}...
""".format(node_name, type)

        mel.eval("""
        defaultNavigation -createNew -destination "{1}.{0}";
        createRenderNode -allWithTexturesUp "defaultNavigation -force true -connectToExisting -source %node -destination {1}.{0}" "";
        defaultNavigation -defaultTraversal -destination "{1}.{0}";
        """.format(type, node_name))

        file_name = mel.eval('shadingNode -asTexture file;')
        texture_name = mel.eval('shadingNode -asUtility place2dTexture;')

        print """
-- More modifications on shader file {0} and texture {1}...
""".format(file_name, texture_name)

        mel.eval("""
        shadingNode -asUtility place2dTexture;
        connectAttr -f {1}.coverage {0}.coverage;
        connectAttr -f {1}.translateFrame {0}.translateFrame;
        connectAttr -f {1}.rotateFrame {0}.rotateFrame;
        connectAttr -f {1}.mirrorU {0}.mirrorU;
        connectAttr -f {1}.mirrorV {0}.mirrorV;
        connectAttr -f {1}.stagger {0}.stagger;
        connectAttr -f {1}.wrapU {0}.wrapU;
        connectAttr -f {1}.wrapV {0}.wrapV;
        connectAttr -f {1}.repeatUV {0}.repeatUV;
        connectAttr -f {1}.offset {0}.offset;
        connectAttr -f {1}.rotateUV {0}.rotateUV;
        connectAttr -f {1}.noiseUV {0}.noiseUV;
        connectAttr -f {1}.vertexUvOne {0}.vertexUvOne;
        connectAttr -f {1}.vertexUvTwo {0}.vertexUvTwo;
        connectAttr -f {1}.vertexUvThree {0}.vertexUvThree;
        connectAttr -f {1}.vertexCameraOne {0}.vertexCameraOne;
        connectAttr {1}.outUV {0}.uv;
        connectAttr {1}.outUvFilterSize {0}.uvFilterSize;
        defaultNavigation -force true -connectToExisting -source {0} -destination {3}.{2}; window -e -vis false createRenderNodeWindow;
        connectNodeToAttrOverride("{0}", "{3}.{2}");
        setAttr "{0}.filterType" 0;
        """.format(file_name, texture_name, type, node_name))

        if type == 'diffuse':
            cmds.setAttr('{0}.fileTextureName'.format(file_name), '{0}/{1}-TM_u0_v0.tif'.format(os.getcwd(), group_name), type='string')
        elif type == 'standard_bump':
            shadingnode_name = mel.eval('shadingNode -asUtility bump2d')
            mel.eval("""
            setAttr {0}.alphaIsLuminance true;
            connectAttr -f {0}.outAlpha {4}.bumpValue;
            connectAttr -f {4}.outNormal {3}.{2};
            setAttr "{4}.bumpInterp" 1;
            """.format(file_name, texture_name, type, node_name, shadingnode_name))
            cmds.setAttr('{0}.fileTextureName'.format(file_name), '{0}/{1}-NM_u0_v0.tif'.format(os.getcwd(), group_name), type='string')


print 'Opening files...'

os.chdir('{0}{1}'.format(project_path, sub_path))
root = os.getcwd()
for root, dir_names, file_names in os.walk(root):

    print 'Looping through groups...'

    # Note: There's two levels of groups here.
    for group_name in dir_names:

        asset_dir = '{0}/{1}/export'.format(root, group_name)
        if not os.path.isdir(asset_dir):
            continue
        os.chdir(asset_dir)

        print 'Group {0}:'.format(group_name)

        for _root, _dir_names, _file_names in os.walk(os.getcwd()):

            print 'Looping through assets...'

            for file_name in _file_names:

                (short_name, extension) = os.path.splitext(file_name)
                if extension != '.OBJ' or short_name.endswith('_copy'):
                    continue

                print """
-- Adding exported asset {0}...
""".format(file_name)

                mel.eval("""
file -import -type "OBJ" -ra true -namespace "{2}" -options "mo=1"  -pr -loadReferenceDepth "all" "{0}/{1}";
""".format(_root, file_name, short_name))

                runFileOperations(short_name)

print 'Done!'
