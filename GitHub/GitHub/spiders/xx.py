import os
path=r'e://scrapy/GitHub/GitHub/media/people'
def x():
    count = 0
    for root, dirs, files in os.walk(path):
        #print files
        fileLength = len(files)
        if fileLength != 0:
            count = count + fileLength
 
    print "The number of files under <%s> is: %d" %(path,count)

