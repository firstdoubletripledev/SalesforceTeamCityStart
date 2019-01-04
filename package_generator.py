import os.path
import os
import subprocess
import configparser
import logging
import shutil
from xml.dom import minidom
from git import Repo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 
c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

# BUILD_FOLDER = os.path.join(os.environ['system.teamcity.build.workingDir'],'src')
WORKING_DIR = os.path.normpath(os.path.dirname(__file__))
BUILD_FOLDER = os.path.join(WORKING_DIR,'deploy')
PACKAGE_XML = os.path.join(WORKING_DIR,'package.xml')
DESTRUCTIVE_XML = os.path.join(WORKING_DIR,'destructiveChangesPost.xml')
TEMPLATE_XML = os.path.join(WORKING_DIR,'packagexml_template.xml')

def describe_metadata(config):
    result = subprocess.run(["ant","describeMetadata"],text=True,capture_output=True)
    replaced = result.stdout.replace('*','')
    s = replaced.replace('[sf:describeMetadata]','').splitlines()
    xmlNames = [st.replace('XMLName','').replace(':','').strip() for st in s if 'XMLName' in st]
    dirNames = [st.replace('DirName','').replace(':','').strip() for st in s if 'DirName' in st]
    
    config['MAPPING'] = dict(zip(dirNames,xmlNames))
    with open('config.ini','w') as configfile:
        config.write(configfile)    

def get_members(config):
    repo = Repo(WORKING_DIR)
    repo.git.checkout(config['CI']['BRANCH_NAME'])
    logger.debug(f'Getting files from commit on branch {config["CI"]["BRANCH_NAME"]}')

    head_commit = repo.commit('HEAD')
    
    deleted = []
    if len(head_commit.parents) > 0:
        previous_commit = repo.commit('HEAD~1')
        deleted = [ item.a_path for item in previous_commit.diff(head_commit).iter_change_type('D')]

    changed_result = { md_type:[] for md_type in config['MAPPING']}
    deleted_result = { md_type:[] for md_type in config['MAPPING']}
    metadata_ext = ['.cls','.trigger','.component','.page']

    for file_path in head_commit.stats.files.keys():
        try:
            if not file_path.endswith('.xml') and 'src' in file_path:
                splitted_path = file_path.split('/')
                path = splitted_path[1:-1]
                md_type = splitted_path[1]
                file = os.path.splitext(splitted_path[-1])
                file_name = file[0]
                file_ext = file[1]

                if file_path in deleted:
                     deleted_result[md_type].append(file_name)
                else:
                    move_to_deploy(file_path,path,BUILD_FOLDER)
                    changed_result[md_type].append(file_name)
                    if file_ext in metadata_ext:
                        md_ext = file_ext + '-meta.xml'
                        md_name = file_name + md_ext
                        splitted_path[-1] = md_name
                        md_path = os.path.join('',*splitted_path)
                        move_to_deploy(md_path,path,BUILD_FOLDER)

            # if not file_path.endswith('.xml') and 'src' in file_path:
            #     splitted_line = file_path.split('/')
            #     md_type = splitted_line[-2].lower()
            #     member = splitted_line[-1]
            #     if file_path in deleted:
            #         deleted_result[md_type].append(os.path.splitext(member)[0])
            #     else:
            #         move_to_deploy(file_path,BUILD_FOLDER)
            #         changed_result[md_type].append(os.path.splitext(member)[0])
        except KeyError:
            logger.debug('KeyError, not found metadata type')
            pass
    return (changed_result, deleted_result)

def move_to_deploy(file_path,path,dst):
    dst = os.path.normpath(os.path.join(dst,*path))
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.copy(os.path.normpath(os.path.join(WORKING_DIR,file_path)),dst)



def write_type(xml,type_name, members,path):
    root = xml.getElementsByTagName('Package')[0]
    root = xml.documentElement

    def createTextElement(xml,parent,tag,value):
        element = xml.createElement(tag)
        text = xml.createTextNode(value)
        element.appendChild(text)
        parent.appendChild(element)

    with open(path,'w') as writer:
        type_elem = xml.createElement('types')
        root.appendChild(type_elem)

        for member in members:
            createTextElement(xml,type_elem,'members',member)
        createTextElement(xml,type_elem,'name',type_name)

        pretty_xml = xml.toprettyxml()
        writer.write(pretty_xml)

def generate_package_xml(config):
    logger.debug('Start generating package.xml')
    commit_mdt = get_members(config)    

    def write_members(template_path, items, result_path):
        template_xml = minidom.parse(template_path)
        for mdt_type, members in items:
            if members:
                write_type(template_xml,config['MAPPING'][mdt_type],members,result_path)

    write_members(TEMPLATE_XML,commit_mdt[0].items(),PACKAGE_XML)
    write_members(TEMPLATE_XML,commit_mdt[1].items(),DESTRUCTIVE_XML)


    if os.path.exists(os.path.abspath(PACKAGE_XML)):
        splitted_package = os.path.split(PACKAGE_XML)[1]
        os.replace(PACKAGE_XML, os.path.join(BUILD_FOLDER,splitted_package))

    # for fdir in PACKAGE_XML, DESTRUCTIVE_XML:
    #     if os.path.exists(os.path.abspath(fdir)):
    #         os.replace(fdir, os.path.join(BUILD_FOLDER,fdir))
    #     elif fdir == PACKAGE_XML:
    #         copyfile(TEMPLATE_XML,os.path.join(BUILD_FOLDER, PACKAGE_XML))


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.join(WORKING_DIR,'config.ini'))
    if os.path.exists(BUILD_FOLDER):
        shutil.rmtree(BUILD_FOLDER)
    # if not config.has_section('MAPPING'):
    #     describe_metadata(config)
    generate_package_xml(config)
        
