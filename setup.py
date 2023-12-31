from setuptools import find_packages,setup
from typing import List
import os,time,subprocess,sys

HYPEN_E_DOT = "-e ."

def get_requirements(file_path:str) -> List[str]:
    requirements=[]
    with open(file_path) as file:
        requirements = file.readlines()
        requirements = [req.replace('\n','') for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)

        return requirements


def load_spacy():
    print("Loading spacy dependencies.....")
    
    virtual_env_path = "./venv"
    # activate_script = os.path.join(virtual_env_path, "Scripts", "activate")
    # subprocess.run([activate_script], shell=True, text=True)
    os.environ['PATH'] = f"{virtual_env_path}\\Scripts;{os.environ['PATH']}"
    
    print(subprocess.run([sys.executable, "-m", "spacy", "download", 'en_core_web_lg'], text=True))


    print("Loaded Sucessfully")
   
def intall_ffmpeg():
    print('Installing ffmpeg and ffprobe dependencies ............')
    try:
        # # Run "apt install ffmpeg and ffprobe "
        
        # print(subprocess.run([sys.executable, "pip", "install", "pydub"], text=True))
        print(subprocess.run(["sudo", "apt", "install", "ffmpeg"], capture_output=True, text=True))
        print("ffmpeg and ffprobe installed successfully.")
        
        virtual_env_path = "./venv"
        lib_path = "/usr/bin/ffmpeg"
        # lib_path = "/usr/local/bin/ffmpeg"
        # lib_path = "/opt/ffmpeg/bin/ffmpeg"

        import pydub,ffmpeg 
        ffmpeg_binary = f"{lib_path}"
        ffprobe_binary = "/usr/bin//ffprobe"
        pydub.AudioSegment.ffmpeg = ffmpeg_binary
        ffmpeg.input.ffmpeg = ffmpeg_binary
        pydub.AudioSegment.ffprobe = ffprobe_binary
        ffmpeg.input.ffprobe = ffprobe_binary

        print("ffmpeg and ffprobe setup done completely.")

    except Exception as e:
       print('Error :', e)
       print('Installing Unsucessful.')

setup(
    name = "YoutubeTranscription",
    version= '0.0.1',
    author= 'Manish',
    author_email="manish.rai709130@gmail.com",
    install_requires = get_requirements('requirements.txt'),
    packages= find_packages(),
)

print("Loading custom Dependencies from setup.py ")
load_spacy()
intall_ffmpeg()