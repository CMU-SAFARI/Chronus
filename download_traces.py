import wget

url = 'https://zenodo.org/records/14281771/files/cputraces.tar.gz?download=1'

wget.download(url, 'cputraces.tar.gz')