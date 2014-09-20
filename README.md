Source code for pypisearch.linuxcoder.co.uk

Download list of pypi packages and use local elasticsearch instance to search them

Usage:

    * clone repo somewhere and cd there
    * virtualenv -p python3 .
    * . ./bin/activate
    * pip install -r requirements.txt
    * edit config.py
    * run python get.py to download pypi packages. This may take long time (~50k http requests)
      If it fails, just run it again.
    * Run python update.py to load downloaded data into ES.
    * Run python webapp.py and go to http://localhost:5000/.

Requirements:

    * python3
    * elasticsearch

Usage:

    
