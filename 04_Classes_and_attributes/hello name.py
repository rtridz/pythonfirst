    #!/usr/bin/python
    # -*- coding: UTF-8 -*-
     
    import sys
    import argparse
     
    def createParser ():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-n', '--name')
     
        return parser
     
     
    if __name__ == '__main__':
        parser = createParser()
        namespace = parser.parse_args(sys.argv[1:])
     
        print ("Привет, {}!".format (namespace.name) )
