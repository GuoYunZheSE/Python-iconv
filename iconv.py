import codecs
import argparse
import tqdm
import psutil
import concurrent.futures
import uuid
import os

class EncodeError(Exception):
    def __init__(self,file:str):
        self.message = f"can not find coding style for {file}"
        self.file=file
    def __str__(self):
        return f"EncodeError: Can not determining encoding for file:'{self.file}'"
def GetFilesList(directory:str)->[]:
    file_list=[]
    total_size=0
    for root_path, sub_path, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root_path, file)
            # print(f"Find File:{file_path}")
            file_list.append(file_path)
            total_size+=os.path.getsize(file_path)
    return [file_list,total_size]

def EncodeTransferWithThreadPool(file_list:[str],worker:int,memory_size,total_size,origin:str or None,dst:str):
    params=[]
    for file in  file_list:
        file_size=os.path.getsize(file)
        read_size=max(int(memory_size*file_size/total_size),int(memory_size/worker))
        param={
            "read_size": read_size,
            "file_path": file,
            "origin": origin,
            "dst": dst,
        }
        # print("File:{}\tSize:{:.2f}MB\tRead:{:.2f}MB".format(file,file_size>>20,read_size>>20))
        params.append(param)
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as executor:
        res = list(tqdm.tqdm(executor.map(EncodeTransfer,params),total=len(params)))

def EncodeTransfer(params:{})->None:
    try:
        file_path = params["file_path"]
        origin = params["origin"]
        dst = params["dst"]
        read_size = params["read_size"]

        f_r=""
        temp_name = file_path + uuid.uuid4().__str__()
        if origin:
            f_r=codecs.open(file_path,"r",encoding=origin)
        else:
            for code_style in ["utf-8","utf-16","gb18030","ascii"]:
                # Determining Coding Style
                try:
                    f_r = codecs.open(file_path, "r", encoding=code_style)
                    f_r.read(1024)
                except Exception:
                    f_r.close()
                    continue

                f_r = codecs.open(file_path, "r", encoding=code_style)
                break
            if f_r.closed:
                raise EncodeError(file=file_path)
        f_w=codecs.open(temp_name,"w",encoding=dst)

        info = f_r.read(read_size)
        while info:
            f_w.write(info)
            info=f_r.read(read_size)
        f_w.close()
        f_r.close()
        os.remove(file_path)
        os.rename(temp_name,file_path)
        # print(f"Done:{file_path}")
    except EncodeError as e:
        print(str(e))
    except Exception:
        os.remove(temp_name)

def Transfer(filepath:str,origin:str or None,dst:str):
    # The Path is a directory
    if os.path.isdir(filepath):
        print(f"Dir {filepath} Found")
        file_list,total_size=GetFilesList(filepath)
    # The Path is a single file
    elif os.path.isfile(filepath):
        print(f"File {filepath} Found")
        file_list,total_size=[filepath],os.path.getsize(filepath)
    else:
        raise FileNotFoundError
    run_time={
        "MemorySize":psutil.virtual_memory()[0],
        "Core":psutil.cpu_count()*2
    }
    if len(file_list)==1:
        params = {
            "read_size": run_time['MemorySize'],
            "file_path": file_list[0],
            "origin":origin,
            "dst":dst,
        }
        EncodeTransfer(params)
    else:
        EncodeTransferWithThreadPool(file_list,run_time['Core'],run_time["MemorySize"],total_size,origin,dst)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="iconv")
    parser.add_argument("-p","--path",metavar="path",dest="file_path",required=True,help="The directory or file path")
    parser.add_argument("-o", "--origin", metavar="origin", dest="origin", required=False,
                        help="The origin file encode")
    parser.add_argument("-d", "--dst", metavar="destination", dest="des", required=True,
                        help="The destination file encode")
    args = parser.parse_args()
    file_path = args.file_path
    origin =args.origin
    dst =args.des
    Transfer(file_path,origin,dst)
