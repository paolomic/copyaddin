import os
import sys
import re
import gzip
import shutil
from datetime import datetime
from pathlib import Path

def GetAddinListFromBootFile() -> list:
    """Extract addin name-version pairs from bootstrap log file"""
    pattern = r'\[App\.AddinMgr\] Loaded AddIn (\w+) \(ver\. ([\d\.]+)(?:\.)?d(\d+)\)'
    result = []
    
    logs = list(Path('.').glob('Bootstrap_*.log'))
    if not logs:
        raise FileNotFoundError("No Bootstrap log file found")
    latest_log = max(logs, key=lambda p: p.name)
    
    with open(latest_log, 'r') as f:
        for line in f:
            if match := re.search(pattern, line):
                name, ver, dev = match.groups()
                version = f"{ver}.{dev}"
                result.append((name, version))
    
    return result


def GetAddinListFromModuleFile(extension=False):
    filename = r'.\ModuleList.txt'
    modules = []
    with open(filename, 'r') as file:
        content = file.read()
        module_sections = content.split('Module ')[1:]
        
        for section in module_sections:
            original_filename_line = [line for line in section.split('\n') if 'Original Filename:' in line]
            if original_filename_line:
                nome = original_filename_line[0].split(':')[1].strip()
                
                # Gestione dell'estensione in base al parametro
                if not extension:
                    nome = nome.split('.')[0]
            
            version_line = [line for line in section.split('\n') if 'FileVer:' in line]
            if version_line:
                versione = version_line[0].split(':')[1].strip()
                
                modules.append((nome, versione))
        
    return modules


def SyncAddinFromBoot(addin_list: list):
    """Sync addins from archive to copy folder based on version list"""
    #TARGET_DIR = r'C:\Users\Paolo\OneDrive - ION\Desktop\History'
    TARGET_DIR = r'V:\rel\Coherence\6.0.0\x64\historic-bin'
    COPY_DIR = Path('copy')
    ORIG_DIR = COPY_DIR / 'orig'
    LOG_FILE = COPY_DIR / 'copyaddin.log'
    
    if COPY_DIR.exists():
        shutil.rmtree(COPY_DIR)
    COPY_DIR.mkdir()
    ORIG_DIR.mkdir()
    
    with open(LOG_FILE, 'w') as log:
        log.write(f"Sync started at {datetime.now()}\n\n")
    
    target_files = list(Path(TARGET_DIR).glob('*'))
    
    for name, version in addin_list:
        copied_files = []
        # Using raw string to avoid double escaping
        version_parts = version.split('.')
        version_parts = version.split('.')
        version_parts = version.split('.')
        
        pattern = rf"{name}(?:\.)?{version_parts[0]}"
        pattern += rf"\.{version_parts[1]}"
        pattern += rf"\.{version_parts[2]}"
        pattern += rf"(?:\.)?d{version_parts[3]}.*"

        matching_files = [f for f in target_files 
                         if re.match(pattern, f.name, re.IGNORECASE)]
        
        for src_file in matching_files:
            shutil.copy2(src_file, ORIG_DIR)
            
            if src_file.name.endswith('.gz'):
                with gzip.open(src_file, 'rb') as gz:
                    base_name = re.sub(rf'(?:\.)?{version}', '', src_file.stem)
                    dest_file = COPY_DIR / base_name
                    
                    with open(dest_file, 'wb') as out:
                        shutil.copyfileobj(gz, out)
                        copied_files.append(dest_file.name)
            else:
                base_name = re.sub(rf'(?:\.)?{version}', '', src_file.name)
                dest_file = COPY_DIR / base_name
                shutil.copy2(src_file, dest_file)
                copied_files.append(dest_file.name)
        
        with open(LOG_FILE, 'a') as log:
            log.write(f"{name} - {version}:\n")
            for file in copied_files:
                log.write(f"  {file}\n")
            log.write("\n")



def _DEBUG():
    return
    print(re.match('MetaMarket\.6\.8\.1\.?d16.*', 'MetaMarket.6.8.1d16.fta' ))
    print(re.match('MetaMarket\.6\.8\.1d16.*' , 'MetaMarket.6.8.1d16.fta', re.IGNORECASE))
    print(re.match('MetaMarket.6', 'MetaMarketx6', re.IGNORECASE))
    

""" def main():
    if len(sys.argv) == 1:
        print("copyaddin syntax:")
        print("   copyaddin m/b")
        print("   m: loads ModuleList.txt - b: loads Bootstrap_xxxxxxxx.log")
    else:
        comp_list = []
        if(sys.argv[1]=='b'):
            comp_list = GetAddinListFromBootFile()
        else:
            comp_list = GetAddinListFromModuleFile()
        SyncAddinFromBoot(comp_list)
 """

def print_hyperlink(pref, path):
    # Converte il percorso in un hyperlink cliccabile per Windows
    full_path = os.path.abspath(path)
    print(pref, end='')
    print(f'\x1b]8;;file:///{full_path}\x1b\\{path}\x1b]8;;\x1b\\')


def main():
    print("COPYADDIN: Select Component Source:")
    print("   [M]: ModuleList.txt")
    print("   [B]: Bootstrap_xxxxxxxx.log")

    key =  input(f'')

    comp_list = []
    if(key.upper()=='B'):
        comp_list = GetAddinListFromBootFile()
    if(key.upper()=='M'):
        comp_list = GetAddinListFromModuleFile()
    print('Working ...')
    SyncAddinFromBoot(comp_list)
    print(f'log (CTRL-Click):')
    print_hyperlink('   ', r'copy\copyaddin.log')
    print('Done')

if __name__ == "__main__":
    main()
    