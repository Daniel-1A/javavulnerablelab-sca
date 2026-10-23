"""Descarga reanudable de feeds públicos NVD con comprobación SHA-256 oficial."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
import math
import re
import time
import urllib.request

BASE=Path(sys.argv[1]) if len(sys.argv)>1 else Path('target/nvd-feeds')
BASE.mkdir(exist_ok=True)
CHUNK=524288
YEARS=[str(y) for y in range(2002,datetime.now(timezone.utc).year+1)]+['modified']
ROOT='https://nvd.nist.gov/feeds/json/cve/2.0/'

def fetch(url,headers=None):
    error=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'University-SCA-Laboratory/1.0','Accept-Encoding':'identity',**(headers or {})})
            with urllib.request.urlopen(req,timeout=25) as r:
                status=r.status;content_range=r.headers.get('Content-Range');data=r.read()
            return status,content_range,data
        except Exception as e:
            error=e
            time.sleep(min(2**attempt,8))
    raise error

def metadata(year):
    name='nvdcve-2.0-'+year
    _,_,data=fetch(ROOT+name+'.meta')
    (BASE/(name+'.meta')).write_bytes(data)
    values=dict(line.split(':',1) for line in data.decode().splitlines() if ':' in line)
    return name,values

def part(task):
    name,index,size=task
    start=index*CHUNK;end=min(start+CHUNK,size)-1
    path=BASE/(name+'.part'+str(index))
    if path.exists() and path.stat().st_size==end-start+1:return name
    status,content_range,data=fetch(ROOT+name+'.json.gz',{'Range':f'bytes={start}-{end}'})
    if status!=206 or content_range!=f'bytes {start}-{end}/{size}' or len(data)!=end-start+1:
        raise ValueError(f'Invalid HTTP range for {name} chunk {index}: {status}, {content_range}, {len(data)}')
    path.write_bytes(data)
    return name

def verify(path,meta):
    digest=hashlib.sha256();size=0
    with gzip.open(path,'rb') as f:
        while block:=f.read(1048576):digest.update(block);size+=len(block)
    return size==int(meta['size']) and digest.hexdigest().upper()==meta['sha256'].upper()

def main():
    key=os.environ.get('NVD_API_KEY','')
    if not key:raise SystemExit('Falta el secreto NVD_API_KEY.')
    request=urllib.request.Request('https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=1',headers={'apiKey':key,'User-Agent':'University-SCA-Laboratory/1.0'})
    try:
        with urllib.request.urlopen(request,timeout=30) as response:
            if response.status!=200:raise SystemExit('NVD no acepto la clave configurada.')
            response.read()
    except Exception as error:
        raise SystemExit('No se pudo validar la clave NVD: '+type(error).__name__) from None
    print('NVD_API_KEY validada con NVD; su valor no se imprime.',flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:metas=dict(pool.map(metadata,YEARS))
    tasks=[];remaining={};complete=[]
    for name,meta in metas.items():
        output=BASE/(name+'.json.gz')
        if output.exists() and verify(output,meta):
            complete.append(name);continue
        size=int(meta['gzSize']);count=math.ceil(size/CHUNK);remaining[name]=count
        tasks.extend((name,i,size) for i in range(count))
    print(json.dumps({'files':len(metas),'download_mb':round(sum(int(m['gzSize']) for n,m in metas.items() if n not in complete)/1048576,1),'chunks':len(tasks),'workers':8}),flush=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(part,t) for t in tasks]
        for future in as_completed(futures):
            name=future.result();remaining[name]-=1
            if remaining[name]==0:
                meta=metas[name];output=BASE/(name+'.json.gz');count=math.ceil(int(meta['gzSize'])/CHUNK)
                with output.open('wb') as f:
                    for i in range(count):f.write((BASE/(name+'.part'+str(i))).read_bytes())
                if not verify(output,meta):raise ValueError('SHA256 mismatch: '+name)
                complete.append(name)
                # Solo elimina los fragmentos temporales propios tras verificar el archivo completo.
                for i in range(count):(BASE/(name+'.part'+str(i))).unlink()
                print(f'VERIFICADO {len(complete)}/{len(metas)} {name}',flush=True)
    manifest={'source':ROOT,'verification':'SHA-256 del JSON descomprimido y longitud contra .meta oficial del NVD','files':metas}
    (BASE/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Todos los feeds NVD completos y verificados.',flush=True)

if __name__=='__main__':main()
