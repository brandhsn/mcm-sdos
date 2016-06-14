# MCM-SDOS
The Secure Delete Object Store - part of the Micro Content Management system (MCM)

MCM consists of multiple components that form a small experimental content management system.

The Secure Delete Object Store (SDOS) implements a key management mechanism that enables cryptographic deletion of objects. 
SDOS is implemented as an API proxy for the Swift object store from the OpenStack project. SDOS can be used with any unmodified Swift client and server.

## How to use
you can either manually run one of the test/experimental classes:

    . setenv.sh
    python mcm/sdos/tester/PerfTest.py
    python mcm/sdos/tester/GeomTest.py


or start it as a service that offers the Swift API proxy to which your Swift clients can connect:
    
    . setenv.sh
    python runService_Development.py
    
    
### configuration
is currently done by setting parameters in

     mcm/sdos/configuration.py


## Dev setup
### first setup after new checkout
make sure to specify a python 3 or higher interpreter for your virtualenv (SDOS doesn't support python 2)
in the main directory


    virtualenv venvSDOS
    . setenv.sh
    (included in setenv) source venvSDOS/bin/activate
    pip install -r requirements.txt
    

 
to leave venv

    deactivate
  
    
### use pip to install requirements
just install the existing reqs

    pip install -r requirements.txt
    
install new packages

    pip install <package>


save new packages to requirements:

    pip freeze --local > requirements.txt